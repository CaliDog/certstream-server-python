import asyncio
import logging
import json

import math
import sys

import datetime
from collections import deque

import requests
import base64
import os
import time

import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import aiohttp
from aiohttp import web

from collections import OrderedDict
from OpenSSL import crypto
from construct import Struct, Byte, Int16ub, Int64ub, Enum, Bytes, \
    Int24ub, this, GreedyBytes, GreedyRange, Terminated, Embedded

MerkleTreeHeader = Struct(
    "Version"         / Byte,
    "MerkleLeafType"  / Byte,
    "Timestamp"       / Int64ub,
    "LogEntryType"    / Enum(Int16ub, X509LogEntryType=0, PrecertLogEntryType=1),
    "Entry"           / GreedyBytes
)

Certificate = Struct(
    "Length" / Int24ub,
    "CertData" / Bytes(this.Length)
)

CertificateChain = Struct(
    "ChainLength" / Int24ub,
    "Chain" / GreedyRange(Certificate),
)

PreCertEntry = Struct(
    "LeafCert" / Certificate,
    Embedded(CertificateChain),
    Terminated
)

with open('html/_site/index.html', 'r') as f:
    index_html = f.read()

class TransparencyWatcher():
    BAD_CT_SERVERS = [
        'ct.izenpe.com',
        'ctserver.cnnic.cn',
        'log.certly.io',
        'ctlog.wosign.com',
    ]

    MAX_BLOCK_SIZE = 64

    def __init__(self, loop, app):
        self.loop = loop
        self.stopped = False

        self.recently_seen = deque(maxlen=25)

        app.router.add_get('/', self.websocket_handler)
        app.router.add_get("/latest.json", self.recently_seen_handler)
        app.router.add_get("/example.json", self.example_message)

        self.queues = []
        logging.info("Initializing the watcher")
        logging.info("Websockets listening on port {}".format(int(os.environ.get('PORT', 8765))))

    async def recently_seen_handler(self, request):
        return web.Response(
            body=json.dumps(
                {
                    "messages": list(self.recently_seen)
                },
                indent=4
            ),
            content_type="application/json",
            headers={
                "Access-Control-Allow-Origin": "*"
            }
        )

    async def example_message(self, request):
        return web.Response(
            body=json.dumps(list(self.recently_seen)[0], indent=4),
            content_type="application/json"
        )

    async def websocket_handler(self, request):

        if request.headers.get("Upgrade"):
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            queue = asyncio.Queue()
            self.queues.append(queue)

            try:
                while True:
                    message = await queue.get()
                    message_json = json.dumps(message)
                    await ws.send_str(message_json)
            except asyncio.CancelledError:
                print('websocket cancelled')
            finally:
                self.queues.remove(queue)

            await ws.close()
            return ws
        else:
            return web.Response(body=index_html, content_type="text/html")

    async def ws_heartbeats(self):
        logging.info("Starting WS heartbeat coro...")
        while True:
            await asyncio.sleep(10)
            logging.debug("Sending ping...")
            timestamp = time.time()
            for queue in self.queues:
                await queue.put({
                    "message_type": "heartbeat",
                    "timestamp": timestamp
                })

    def initialize_ts_lists(self):
        try:
            self.transparency_lists = requests.get('https://www.certificate-transparency.org/known-logs/all_logs_list.json?attredirects=0').json()
        except Exception as e:
            logging.fatal("Invalid response from certificate directory! Exiting :(")
            sys.exit(1)

        logging.info("Retrieved transparency list with {} entries to watch.".format(len(self.transparency_lists['logs'])))
        for entry in self.transparency_lists['logs']:
            logging.info("  + {}".format(entry['description']))

    async def run(self):
        self.initialize_ts_lists()
        coroutines = [self.watch_for_updates_task(operator) for operator in self.transparency_lists['logs']
                      if operator['url'] not in self.BAD_CT_SERVERS]
        coroutines.append(self.ws_heartbeats())

        await asyncio.gather(*coroutines)

    def stop(self, loop):
        logging.info('Got stop order, exiting...')
        self.stopped = True
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def _dump_extensions(self, certificate):
        extensions = {}
        for x in range(certificate.get_extension_count()):
            extension_name = ""
            try:
                extension_name = certificate.get_extension(x).get_short_name()

                if extension_name == b'UNDEF':
                    continue

                extensions[extension_name.decode('latin-1')] = certificate.get_extension(x).__str__()
            except:
                try:
                    extensions[extension_name.decode('latin-1')] = "NULL"
                except Exception as e:
                    logging.debug("Extension parsing error -> {}".format(e))
        return extensions

    def _dump_cert(self, certificate):
        subject = certificate.get_subject()
        not_before_datetime = datetime.datetime.strptime(certificate.get_notBefore().decode('ascii'), "%Y%m%d%H%M%SZ")
        not_after_datetime = datetime.datetime.strptime(certificate.get_notAfter().decode('ascii'), "%Y%m%d%H%M%SZ")
        return {
            "subject": {
                "aggregated": repr(certificate.get_subject())[18:-2],
                "C": subject.C,
                "ST": subject.ST,
                "L": subject.L,
                "O": subject.O,
                "OU": subject.OU,
                "CN": subject.CN
            },
            "extensions": self._dump_extensions(certificate),
            "not_before": not_before_datetime.timestamp(),
            "not_after": not_after_datetime.timestamp(),
            "as_der": base64.b64encode(crypto.dump_certificate(crypto.FILETYPE_ASN1, certificate)).decode('utf-8')
        }

    def _add_all_domains(self, cert_data):
        all_domains = []

        # Apparently we have certificates with null CNs....what?
        if cert_data['leaf_cert']['subject']['CN']:
            all_domains.append(cert_data['leaf_cert']['subject']['CN'])

        SAN = cert_data['leaf_cert']['extensions'].get('subjectAltName')

        if SAN:
            for entry in SAN.split(', '):
                if entry.startswith('DNS:'):
                    all_domains.append(entry.replace('DNS:', ''))

        cert_data['leaf_cert']['all_domains'] = list(OrderedDict.fromkeys(all_domains))

        return cert_data

    async def watch_for_updates_task(self, operator_information):
        latest_size = 0
        name = operator_information['description']
        while not self.stopped:
            try:
                async with aiohttp.ClientSession(loop=self.loop) as session:
                    async with session.get("http://{}/ct/v1/get-sth".format(operator_information['url'])) as response:
                        info = await response.json()
            except aiohttp.ClientError as e:
                logging.info('[{}] Exception -> {}'.format(name, e))
                await asyncio.sleep(5)
                continue

            tree_size = info.get('tree_size')

            if latest_size == 0:
                latest_size = tree_size

            if latest_size < tree_size:
                logging.info('[{}] [{} -> {}] New certs found, updating!'.format(name, latest_size, tree_size))

                try:
                    async for result_chunk in self.get_new_results(operator_information, latest_size, tree_size):
                        for entry in result_chunk:
                            mtl = MerkleTreeHeader.parse(base64.b64decode(entry['leaf_input']))

                            cert_data = {}

                            if mtl.LogEntryType == "X509LogEntryType":
                                cert_data['type'] = "X509LogEntry"
                                chain = [crypto.load_certificate(crypto.FILETYPE_ASN1, Certificate.parse(mtl.Entry).CertData)]
                                extra_data = CertificateChain.parse(base64.b64decode(entry['extra_data']))
                                for cert in extra_data.Chain:
                                    chain.append(crypto.load_certificate(crypto.FILETYPE_ASN1, cert.CertData))
                            else:
                                cert_data['type'] = "PreCertEntry"
                                extra_data = PreCertEntry.parse(base64.b64decode(entry['extra_data']))
                                chain = [crypto.load_certificate(crypto.FILETYPE_ASN1, extra_data.LeafCert.CertData)]

                                for cert in extra_data.Chain:
                                    chain.append(
                                        crypto.load_certificate(crypto.FILETYPE_ASN1, cert.CertData)
                                    )

                            cert_data.update({
                                "leaf_cert": self._dump_cert(chain[0]),
                                "chain": [self._dump_cert(x) for x in chain[1:]],
                                "cert_index": entry['index'],
                                "seen": time.time()
                            })

                            self._add_all_domains(cert_data)

                            cert_data['source'] = {
                                "url": operator_information['url'],
                                "name": operator_information['description']
                            }

                            await self.push_new_message_to_clients(cert_data)

                except aiohttp.ClientError as e:
                    logging.info('[{}] Exception -> {}'.format(name, e))
                    await asyncio.sleep(5)
                    continue

                latest_size = tree_size
            else:
                logging.debug('[{}][{}|{}] No update needed, continuing...'.format(name, latest_size, tree_size))

            await asyncio.sleep(5)

    async def get_new_results(self, operator_information, latest_size, tree_size):
        # The top of the tree isn't actually a cert yet, so the total_size is what we're aiming for
        total_size = (tree_size - 1) - latest_size
        start = latest_size

        end = start + self.MAX_BLOCK_SIZE

        chunks = math.ceil(total_size / self.MAX_BLOCK_SIZE)

        logging.info("Retrieving {} certificates ({} -> {}) for {}".format(tree_size-latest_size, latest_size, tree_size, operator_information['description']))
        async with aiohttp.ClientSession(loop=self.loop) as session:
            for _ in range(chunks):
                # Cap the end to the last record in the DB
                if end >= tree_size:
                    end = tree_size - 1

                assert end >= start, "End {} is less than start {}!".format(end, start)
                assert end < tree_size, "End {} is less than tree_size {}".format(end, tree_size)

                async with session.get(
                        "http://{}/ct/v1/get-entries?start={}&end={}".format(operator_information['url'],
                                                                              start,
                                                                              end)
                ) as response:
                    certificates = await response.json()
                    if 'error_message' in certificates:
                        print("error!")

                    for index, cert in zip(range(start,end), certificates['entries']):
                        cert['index'] = index

                    yield certificates['entries']

                start += self.MAX_BLOCK_SIZE

                end = start + self.MAX_BLOCK_SIZE + 1

    async def push_new_message_to_clients(self, cert_data):
        data_packet = {
            "message_type": "certificate_update",
            "data": cert_data
        }
        self.recently_seen.append(data_packet)
        for queue in self.queues:
            await queue.put(data_packet)

logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.DEBUG)
logging.info("Starting...")

loop = asyncio.get_event_loop()

app = web.Application(loop=loop)

watcher = TransparencyWatcher(loop, app)


try:
    result = asyncio.ensure_future(watcher.run())
    web.run_app(app, port=int(os.environ.get('PORT', 8080)))
except KeyboardInterrupt:
    watcher.stop(loop)

loop.close()

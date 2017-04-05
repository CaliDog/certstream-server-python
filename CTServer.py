import asyncio
import logging
import json
import requests
import base64
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import websockets
import aiohttp

from collections import OrderedDict
from OpenSSL import crypto
from construct import Struct, Byte, Int16ub, Int64ub, Enum, Bytes, Int24ub, this, GreedyBytes, GreedyRange, Terminated, Embedded

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

class TransparencyWatcher():
    BAD_CT_SERVERS = [
        'ct.izenpe.com',
        'ctserver.cnnic.cn',
        'log.certly.io',
        'ctlog.wosign.com',
    ]
    MAX_BLOCK_SIZE = 64

    def __init__(self, loop):
        self.loop = loop
        self.stopped = False
        self.websocket_coro = websockets.serve(self.ws_handler, 'localhost', 80, loop=self.loop)
        self.queues = []
        logging.info("Initializing the watcher")

    async def ws_handler(self, websocket, path):
        queue = asyncio.Queue()
        self.queues.append(queue)
        while True:
            message = await queue.get()
            try:
                message_json = json.dumps(message)
                await websocket.send(message_json)
            except websockets.ConnectionClosed:
                self.queues.remove(queue)
                return

    def initialize_ts_lists(self):
        self.transparency_lists = requests.get('https://www.certificate-transparency.org/known-logs/log_list.json?attredirects=0').json()
        logging.info("Retrieved transparency list with {} entries to watch.".format(len(self.transparency_lists['logs'])))
        for entry in self.transparency_lists['logs']:
            logging.info("  + {}".format(entry['description']))

    async def run(self):
        self.initialize_ts_lists()
        coroutines = [self.watch_for_updates_task(operator) for operator in self.transparency_lists['logs']
                      if operator['url'] not in self.BAD_CT_SERVERS]

        coroutines.append(self.websocket_coro)

        self.tasks = await asyncio.gather(*coroutines)

    def stop(self, loop):
        logging.info('Got stop order, exiting...')
        self.stopped = True
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def _dump_extensions(self, certificate):
        extensions = {}
        for x in range(certificate.get_extension_count()):
            try:
                extension_name = certificate.get_extension(x).get_short_name()
                if extension_name == b'UNDEF':
                    continue
                extensions[extension_name.decode('utf-8')] = certificate.get_extension(x).__str__()
            except Exception as e:
                identifier = certificate.get_subject().CN.replace(' ', '_')
                logging.error('Exception parsing extensions :( [{}]'.format(identifier))
                cert_der = crypto.dump_certificate(crypto.FILETYPE_ASN1, certificate)
                with open('/tmp/{}.der'.format(identifier), 'wb') as f:
                    f.write(cert_der)
        return extensions

    def _dump_cert(self, certificate):
        subject = certificate.get_subject()
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
            "as_der": base64.b64encode(crypto.dump_certificate(crypto.FILETYPE_ASN1, certificate)).decode('utf-8')
        }

    def _add_all_domains(self, cert_data):
        all_domains = [cert_data['leaf_cert']['subject']['CN'],]

        for entry in cert_data['leaf_cert']['extensions']['subjectAltName'].split(', '):
            if entry.startswith('DNS:'):
                all_domains.append(entry.replace('DNS:', ''))

        cert_data['leaf_cert']['all_domains'] = list(OrderedDict.fromkeys(all_domains))

        return cert_data

    async def watch_for_updates_task(self, operator_information):
        await asyncio.sleep(5)
        latest_size = 0
        name = operator_information['description']
        while not self.stopped:
            try:
                async with aiohttp.ClientSession(loop=self.loop) as session:
                    async with session.get("https://{}/ct/v1/get-sth".format(operator_information['url'])) as response:
                        info = await response.json()
            except aiohttp.ClientError as e:
                logging.info('[{}] Exception -> {}'.format(name, e))
                await asyncio.sleep(5)
                continue

            tree_size = info.get('tree_size')

            if latest_size == 0:
                latest_size = tree_size - 50

            if latest_size < tree_size:
                logging.info('[{}] [{} -> {}] New certs found, updating!'.format(name, latest_size, tree_size))

                try:
                    results = await self.get_new_results(operator_information, latest_size, tree_size)

                    for entry in results:
                        mtl = MerkleTreeHeader.parse(base64.b64decode(entry['leaf_input']))
                        if mtl.LogEntryType == "X509LogEntryType":
                            chain = [crypto.load_certificate(crypto.FILETYPE_ASN1, Certificate.parse(mtl.Entry).CertData)]
                            extra_data = CertificateChain.parse(base64.b64decode(entry['extra_data']))
                            for cert in extra_data.Chain:
                                chain.append(crypto.load_certificate(crypto.FILETYPE_ASN1, cert.CertData))
                        else:
                            extra_data = PreCertEntry.parse(base64.b64decode(entry['extra_data']))
                            chain = [crypto.load_certificate(crypto.FILETYPE_ASN1, extra_data.LeafCert.CertData)]

                            for cert in extra_data.Chain:
                                chain.append(
                                    crypto.load_certificate(crypto.FILETYPE_ASN1, cert.CertData)
                                )

                        cert_data = {
                            "leaf_cert": self._dump_cert(chain[0]),
                            "chain": [self._dump_cert(x) for x in chain[1:]]
                        }
                        self._add_all_domains(cert_data)

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
        results = []
        total_size = tree_size - latest_size
        start = latest_size
        chunks = int((total_size - 1) / self.MAX_BLOCK_SIZE) + 1

        logging.info("Retrieving {} certificates ({} -> {}) for {}".format(tree_size-latest_size, tree_size, latest_size, operator_information['description']))
        async with aiohttp.ClientSession(loop=self.loop) as session:
            for _ in range(chunks):
                if start + self.MAX_BLOCK_SIZE > tree_size:
                    end = tree_size - 1
                else:
                    end = start + self.MAX_BLOCK_SIZE

                async with session.get(
                        "https://{}/ct/v1/get-entries?start={}&end={}".format(operator_information['url'],
                                                                              start,
                                                                              end)
                ) as response:
                    certificates = await response.json()
                    results += certificates['entries']

                start += self.MAX_BLOCK_SIZE + 1

        return results

    async def push_new_message_to_clients(self, cert_data):
        for queue in self.queues:
            await queue.put(cert_data)

logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.DEBUG)
logging.info("Starting...")
loop = asyncio.get_event_loop()

watcher = TransparencyWatcher(loop)

try:
    result = loop.run_until_complete(watcher.run())
except KeyboardInterrupt:
    watcher.stop(loop)

loop.close()

import aiohttp
import asyncio
import logging
import math
import requests
import sys

from certstream.certlib import parse_ctl_entry


class TransparencyWatcher(object):
    BAD_CT_SERVERS = [
        'ct.izenpe.com',
        'ctserver.cnnic.cn',
        'log.certly.io',
        'ctlog.wosign.com',
        "ct1.digicert-ct.com/log",
        "log.certly.io",
        "ct.izenpe.com",
        "ct.ws.symantec.com",
        "ct.wosign.com",
        "vega.ws.symantec.com",
        "ctserver.cnnic.cn",
        "ct.gdca.com.cn",
        "ct.izenpe.eus",
        "ctlog.gdca.com.cn",
        "www.certificatetransparency.cn/ct/",
        "https://ctlog-gen2.api.venafi.com/",
        "sirius.ws.symantec.com",
    ]

    MAX_BLOCK_SIZE = 64

    def __init__(self, _loop):
        self.loop = _loop
        self.stopped = False
        self.queues = []
        self.logger = logging.getLogger('certstream.watcher')

        self.stream = asyncio.Queue()

        self.logger.info("Initializing the CTL watcher")

    def _initialize_ts_lists(self):
        try:
            self.transparency_lists = requests.get('https://www.gstatic.com/ct/log_list/log_list.json').json()
        except Exception as e:
            self.logger.fatal("Invalid response from certificate directory! Exiting :(")
            sys.exit(1)

        self.logger.info("Retrieved transparency list with {} entries to watch.".format(len(self.transparency_lists['logs'])))
        for entry in self.transparency_lists['logs']:
            if entry['url'].endswith('/'):
                entry['url'] = entry['url'][:-1]
            self.logger.info("  + {}".format(entry['description']))

    def get_tasks(self):
        self._initialize_ts_lists()

        coroutines = []
        for log in self.transparency_lists['logs']:
            if log['url'] not in self.BAD_CT_SERVERS:
                coroutines.append(self.watch_for_updates_task(log))
        return coroutines

    def stop(self):
        self.logger.info('Got stop order, exiting...')
        self.stopped = True
        for task in asyncio.Task.all_tasks():
            task.cancel()

    async def watch_for_updates_task(self, operator_information):
        try:
            latest_size = 0
            name = operator_information['description']
            while not self.stopped:
                try:
                    async with aiohttp.ClientSession(loop=self.loop) as session:
                        async with session.get("http://{}/ct/v1/get-sth".format(operator_information['url'])) as response:
                            info = await response.json()
                except aiohttp.ClientError as e:
                    self.logger.info('[{}] Exception -> {}'.format(name, e))
                    await asyncio.sleep(5)
                    continue

                tree_size = info.get('tree_size')

                # TODO: Add in persistence and id tracking per list
                if latest_size == 0:
                    latest_size = tree_size

                if latest_size < tree_size:
                    self.logger.info('[{}] [{} -> {}] New certs found, updating!'.format(name, latest_size, tree_size))

                    try:
                        async for result_chunk in self.get_new_results(operator_information, latest_size, tree_size):
                            for entry in result_chunk:
                                cert_data = parse_ctl_entry(entry, operator_information)
                                await self.stream.put(cert_data)

                    except aiohttp.ClientError as e:
                        self.logger.info('[{}] Exception -> {}'.format(name, e))
                        await asyncio.sleep(5)
                        continue

                    except Exception as e:
                        print(e)
                        sys.exit(1)

                    latest_size = tree_size
                else:
                    self.logger.debug('[{}][{}|{}] No update needed, continuing...'.format(name, latest_size, tree_size))

                await asyncio.sleep(10)
        except Exception as e:
            print(e)
            sys.exit(1)

    async def get_new_results(self, operator_information, latest_size, tree_size):
        # The top of the tree isn't actually a cert yet, so the total_size is what we're aiming for
        total_size = tree_size - latest_size
        start = latest_size

        end = start + self.MAX_BLOCK_SIZE

        chunks = math.ceil(total_size / self.MAX_BLOCK_SIZE)

        self.logger.info("Retrieving {} certificates ({} -> {}) for {}".format(tree_size-latest_size, latest_size, tree_size, operator_information['description']))
        async with aiohttp.ClientSession(loop=self.loop) as session:
            for _ in range(chunks):
                # Cap the end to the last record in the DB
                if end >= tree_size:
                    end = tree_size - 1

                assert end >= start, "End {} is less than start {}!".format(end, start)
                assert end < tree_size, "End {} is less than tree_size {}".format(end, tree_size)

                url = "http://{}/ct/v1/get-entries?start={}&end={}".format(operator_information['url'], start, end)

                async with session.get(url) as response:
                    certificates = await response.json()
                    if 'error_message' in certificates:
                        print("error!")

                    for index, cert in zip(range(start, end+1), certificates['entries']):
                        cert['index'] = index

                    yield certificates['entries']

                start += self.MAX_BLOCK_SIZE

                end = start + self.MAX_BLOCK_SIZE + 1


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    watcher = TransparencyWatcher(loop)
    loop.run_until_complete(asyncio.gather(*watcher.get_tasks()))

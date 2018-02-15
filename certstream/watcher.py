import aiohttp
import asyncio
import logging
import math
import requests
import sys
import os

from certstream.certlib import parse_ctl_entry


class TransparencyWatcher(object):
    # These are a list of servers that we shouldn't even try to connect to. In testing they either had bad
    # DNS records, resolved to un-routable IP addresses, or didn't have valid SSL certificates.
    BAD_CT_SERVERS = [
        "alpha.ctlogs.org",
        "clicky.ct.letsencrypt.org",
        "ct.akamai.com",
        "ct.filippo.io/behindthesofa",
        "ct.gdca.com.cn",
        "ct.izenpe.com",
        "ct.izenpe.eus",
        "ct.sheca.com",
        "ct.startssl.com",
        "ct.wosign.com",
        "ctlog.api.venafi.com",
        "ctlog.gdca.com.cn",
        "ctlog.sheca.com",
        "ctlog.wosign.com",
        "ctlog2.wosign.com",
        "flimsy.ct.nordu.net:8080",
        "log.certly.io",
        "nessie2021.ct.digicert.com/log",
        "plausible.ct.nordu.net",
        "www.certificatetransparency.cn/ct",
    ]

    MAX_BLOCK_SIZE = 64

    def __init__(self, _loop):
        self.loop = _loop
        self.stopped = False
        self.queues = []
        self.logger = logging.getLogger('certstream.watcher')

        self.stream = asyncio.Queue(maxsize=3000)

        self.logger.info("Initializing the CTL watcher")

    def _initialize_ts_logs(self):
        try:
            self.transparency_logs = requests.get('https://www.gstatic.com/ct/log_list/all_logs_list.json').json()
        except Exception as e:
            self.logger.fatal("Invalid response from certificate directory! Exiting :(")
            sys.exit(1)

        self.logger.info("Retrieved transparency log with {} entries to watch.".format(len(self.transparency_logs['logs'])))
        for entry in self.transparency_logs['logs']:
            if entry['url'].endswith('/'):
                entry['url'] = entry['url'][:-1]
            self.logger.info("  + {}".format(entry['description']))

    async def _print_memory_usage(self, tracker):
        while True:
            await asyncio.sleep(60)
            tracker.print_diff()

    def get_tasks(self):
        self._initialize_ts_logs()

        coroutines = []

        if os.getenv("DEBUG_MEMORY", False):
            from pympler.tracker import SummaryTracker
            tracker = SummaryTracker()
            coroutines.append(self._print_memory_usage(tracker))

        for log in self.transparency_logs['logs']:
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
                        async with session.get("https://{}/ct/v1/get-sth".format(operator_information['url'])) as response:
                            info = await response.json()
                except aiohttp.ClientError as e:
                    self.logger.info('[{}] Exception -> {}'.format(name, e))
                    await asyncio.sleep(600)
                    continue

                tree_size = info.get('tree_size')

                # TODO: Add in persistence and id tracking per log
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
                        await asyncio.sleep(600)
                        continue

                    except Exception as e:
                        print("Encountered an exception while getting new results! -> {}".format(e))
                        return

                    latest_size = tree_size
                else:
                    self.logger.debug('[{}][{}|{}] No update needed, continuing...'.format(name, latest_size, tree_size))

                await asyncio.sleep(30)
        except Exception as e:
            print("Encountered an exception while getting new results! -> {}".format(e))
            return

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

                url = "https://{}/ct/v1/get-entries?start={}&end={}".format(operator_information['url'], start, end)

                async with session.get(url) as response:
                    certificates = await response.json()
                    if 'error_message' in certificates:
                        print("error!")

                    for index, cert in zip(range(start, end+1), certificates['entries']):
                        cert['index'] = index

                    yield certificates['entries']

                start += self.MAX_BLOCK_SIZE

                end = start + self.MAX_BLOCK_SIZE + 1

class DummyTransparencyWatcher(object):
    stream = asyncio.Queue()
    def get_tasks(self):
        return []

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    watcher = TransparencyWatcher(loop)
    loop.run_until_complete(asyncio.gather(*watcher.get_tasks()))

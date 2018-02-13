import asyncio
import collections
import json
import logging
import os
import time
import ssl

from aiohttp import web
from aiohttp.web_urldispatcher import Response

from certstream.util import pretty_date, get_ip

WebsocketClientInfo = collections.namedtuple(
    'WebsocketClientInfo',
    ['external_ip', 'queue', 'connection_time', 'channel']
)

STATIC_INDEX = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700" rel="stylesheet">
  </head>
  <body>
    <div id="app"></div>
  <script type="text/javascript" src="https://storage.googleapis.com/certstream-prod/build.js?v={}"></script></body>
</html>
'''.format(time.time())

class WebServer(object):
    def __init__(self, _loop, transparency_watcher):
        self.active_sockets = []
        self.valid_channels = [
            'default',
            'dns-only',
            'leaf-only',
        ]
        self.recently_seen = collections.deque(maxlen=25)
        self.stats_url = os.getenv("STATS_URL", 'stats')
        self.logger = logging.getLogger('certstream.webserver')

        self.loop = _loop
        self.watcher = transparency_watcher

        self.app = web.Application(loop=self.loop)

        self._add_routes()

    def run_server(self):
        self.mux_stream = asyncio.ensure_future(self.mux_ctl_stream())
        self.heartbeat_coro = asyncio.ensure_future(self.ws_heartbeats())

        if os.environ.get("NOSSL", False):
            ssl_ctx = None
        else:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(certfile=os.getenv("SERVER_CERT", "server.crt"), keyfile=os.getenv("SERVER_KEY", "server.key"))

        web.run_app(
            self.app,
            port=int(os.environ.get('PORT', 8080)),
            loop=self.loop,
            ssl_context=ssl_ctx
        )

    def _add_routes(self):
        self.app.router.add_get("/latest.json", self.latest_json_handler)
        self.app.router.add_get("/example.json", self.example_json_handler)
        self.app.router.add_get("/{}".format(self.stats_url), self.stats_handler)
        self.app.router.add_get('/', self.root_handler)
        self.app.router.add_get('/develop', self.dev_handler)

    async def mux_ctl_stream(self):
        while True:
            cert_data = await self.watcher.stream.get()

            data_packet = {
                "message_type": "certificate_update",
                "data": cert_data
            }

            self.recently_seen.append(data_packet)

            for client in self.active_sockets:
                await client.queue.put(data_packet)

    async def dev_handler(self, request):
        # If we have a websocket request
        if request.headers.get("Upgrade"):
            ws = web.WebSocketResponse()

            await ws.prepare(request)

            try:
                for message in self.recently_seen:
                    message_json = json.dumps(message)
                    await ws.send_str(message_json)
            except asyncio.CancelledError:
                print('websocket cancelled')

            await ws.close()

            return ws

        return web.Response(
            body=json.dumps(
                {
                    "error": "Please use this url with a websocket client!"
                },
                indent=4
            ),
            content_type="application/json",
        )

    async def root_handler(self, request, filename=None):
        # If we have a websocket request
        if request.headers.get("Upgrade"):
            requested_channel = request.GET.get('channel', 'default')

            if requested_channel not in self.valid_channels:
                raise web.HTTPBadRequest(text="Invalid channel!")

            ws = web.WebSocketResponse()

            await ws.prepare(request)

            client_queue = asyncio.Queue()

            websocket_info = WebsocketClientInfo(
                external_ip=get_ip(request),
                queue=client_queue,
                connection_time=int(time.time()),
                channel=requested_channel
            )

            self.active_sockets.append(websocket_info)

            try:
                while True:
                    message = await client_queue.get()
                    message_json = json.dumps(message)
                    await ws.send_str(message_json)
            except asyncio.CancelledError:
                print('websocket cancelled')
            finally:
                self.active_sockets.remove(websocket_info)

            await ws.close()

            return ws
        else:
            return Response(body=STATIC_INDEX, content_type="text/html")

    async def latest_json_handler(self, _):
        return web.Response(
            body=json.dumps(
                {
                    "messages": list(self.recently_seen)
                },
                indent=4
            ),
            headers={"Access-Control-Allow-Origin": "*"},
            content_type="application/json",
        )

    async def example_json_handler(self, _):
        if self.recently_seen:
            return web.Response(
                body=json.dumps(list(self.recently_seen)[0], indent=4),
                headers={"Access-Control-Allow-Origin": "*"},
                content_type="application/json",
            )
        else:
            return web.Response(
                body="{}",
                headers={"Access-Control-Allow-Origin": "*"},
                content_type="application/json"
            )

    async def stats_handler(self, _):
        clients = {}
        for client in self.active_sockets:
            client_identifier = "{}-{}".format(client.external_ip, client.connection_time)
            clients[client_identifier] = {
                "ip_address": client.external_ip,
                "conection_time": client.connection_time,
                "connection_length": pretty_date(client.connection_time),
                "channel": client.channel
            }

        return web.Response(
            body=json.dumps({
                    "connected_client_count": len(self.active_sockets),
                    "clients": clients
                }, indent=4
            ),
            content_type="application/json",
        )

    async def ws_heartbeats(self):
        self.logger.info("Starting WS heartbeat coro...")
        while True:
            await asyncio.sleep(10)
            self.logger.debug("Sending ping...")
            timestamp = time.time()
            for client in self.active_sockets:
                await client.queue.put({
                    "message_type": "heartbeat",
                    "timestamp": timestamp
                })

if __name__ == "__main__":
    from certstream.watcher import TransparencyWatcher
    loop = asyncio.get_event_loop()
    watcher = TransparencyWatcher(loop)
    webserver = WebServer(loop, watcher)
    asyncio.ensure_future(asyncio.gather(*watcher.get_tasks()))
    webserver.run_server()

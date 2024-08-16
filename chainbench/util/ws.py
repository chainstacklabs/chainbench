import asyncio
import orjson as json

from autobahn.asyncio import WebSocketClientProtocol, WebSocketClientFactory
from autobahn.websocket.protocol import WebSocketProtocol


def create_protocol(on_connect=None, on_connecting=None, on_message=None, on_open=None, on_close=None):
    member_functions = {}
    if on_connect:
        member_functions["onConnect"] = on_connect
    if on_connecting:
        member_functions["onConnecting"] = on_connecting
    if on_message:
        member_functions["onMessage"] = on_message
    if on_open:
        member_functions["onOpen"] = on_open
    if on_close:
        member_functions["onClose"] = on_close
    return type("WsClientProtocol", (WebSocketClientProtocol,), member_functions)


class WebSocketClient:
    def __init__(self, host, on_connect=None, on_connecting=None, on_message=None, on_open=None, on_close=None):
        self.host = host
        self.factory = WebSocketClientFactory(host)
        self.factory.protocol = create_protocol(on_connect, on_connecting, on_message, on_open, on_close)
        self._loop = asyncio.get_event_loop()
        coro = self._loop.create_connection(self.factory, self.factory.host, self.factory.port, ssl=self.factory.isSecure)
        _, self.protocol = self._loop.run_until_complete(coro)

    def connected(self):
        return self.protocol.state == WebSocketProtocol.STATE_OPEN

    def run_forever(self):
        print("run_forever")
        self._loop.run_forever()

    def close(self):
        self.protocol.sendClose()

    def send(self, data):
        self.protocol.sendMessage(json.dumps(data), isBinary=False)

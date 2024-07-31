import logging
import random
import time

import gevent
import orjson as json
from gevent import Greenlet
from locust import User
from orjson import JSONDecodeError
from tenacity import retry, wait_fixed, retry_if_exception_type, stop_after_attempt
from websocket import WebSocket, WebSocketConnectionClosedException, create_connection


class WssUser(User):
    abstract = True
    logger = logging.getLogger(__name__)
    
    def __init__(self, environment):
        super().__init__(environment)
        self._ws: WebSocket | None = None
        self._ws_greenlet: Greenlet | None = None
        self._requests = {}
        self._running = False
        self.subscriptions = {}

    def on_start(self) -> None:
        self._running = True
        host: str = self.environment.parsed_options.host
        if host.startswith("ws") or host.startswith("wss"):
            self.connect(self.environment.parsed_options.host)
        else:
            raise ValueError("Invalid host provided. Expected ws or wss protocol")
        self.subscribe_all()

    def on_stop(self) -> None:
        self._running = False
        self.unsubscribe_all()
        self.logger.debug("Unsubscribed from all subscriptions")

    def connect(self, host: str, **kwargs):
        self._ws = create_connection(host, **kwargs)
        self._ws_greenlet = gevent.spawn(self.receive_loop)
        if self._ws is not None:
            self.logger.info(f"Connected to {host}")

    def subscribe_all(self):
        subscribe_methods = ["blockSubscribe"]
        for method in subscribe_methods:
            self.subscribe(method)

    def subscribe(self, method: str):
        request_id = random.Random().randint(0, 1000000)
        self.send(
            {
                "id": request_id,
                "jsonrpc": "2.0",
                "method": method,
                "params": [
                    "all",
                    {
                        "commitment": "confirmed",
                        "encoding": "jsonParsed",
                        "showRewards": True,
                        "transactionDetails": "full",
                        "maxSupportedTransactionVersion": 0,
                    },
                ],
            },
            "block_subscribe",
        )
        self._requests[request_id].update({"subscription": method})

    def unsubscribe_all(self):
        subscription_ids = list(self.subscriptions.keys())
        for subscription_id in subscription_ids:
            self.send(
                {
                    "id": random.Random().randint(0, 1000000),
                    "jsonrpc": "2.0",
                    "method": "blockUnsubscribe",
                    "params": [subscription_id],
                },
                "block_unsubscribe",
            )

    def on_message(self, message):
        try:
            response = json.loads(message)
            if "method" in response:
                self.check_subscriptions(response, message)
            else:
                self.check_requests(response, message)
        except JSONDecodeError:
            self.environment.events.request.fire(
                request_type="WSS",
                name="JSONDecodeError",
                response_time=None,
                response_length=len(message),
                exception=JSONDecodeError,
                response=message,
            )

    def check_requests(self, response, message):
        if "id" not in response:
            self.logger.error("Received message without id")
            self.logger.error(response)
            return
        if response["id"] not in self._requests:
            self.logger.error("Received message with unknown id")
            self.logger.error(response)
            return
        request = self._requests.pop(response["id"])
        if request["name"] == "blockSubscribe":
            self.subscriptions.update({response["result"]: request["subscription"]})
        self.environment.events.request.fire(
            request_type="WSS",
            name=request["name"],
            response_time=((time.time_ns() - request["start_time"]) / 1_000_000).__round__(),
            response_length=len(message),
            exception=None,
        )

    def check_subscriptions(self, response, message):
        if response["method"] == "blockNotification":
            if "params" in response:
                if "subscription" in response["params"]:
                    self.environment.events.request.fire(
                        request_type="WSS Sub",
                        name="blockNotification",
                        response_time=time.time().__round__()
                        - response["params"]["result"]["value"]["block"]["blockTime"],
                        response_length=len(message),
                        exception=None,
                    )

    def receive_loop(self):
        try:
            while self._running:
                message = self._ws.recv()
                self.logger.debug(f"WSR: {message}")
                self.on_message(message)
            else:
                self._ws.close()
        except WebSocketConnectionClosedException:
            self.environment.events.request.fire(
                request_type="WS",
                name="WebSocket Connection",
                response_time=None,
                response_length=0,
                exception=WebSocketConnectionClosedException,
            )
            self._running = False
            self.logger.error("Connection closed by server, trying to reconnect...")
            self.on_start()

    def send(self, body, name):
        self._requests.update({body["id"]: {"name": name, "start_time": time.time_ns()}})
        json_body = json.dumps(body)
        self.logger.debug(f"WSS: {json_body}")
        self._ws.send(json_body)

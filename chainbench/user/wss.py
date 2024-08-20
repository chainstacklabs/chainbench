import logging
import time

import gevent
import orjson as json
from gevent import Greenlet, Timeout
from locust import User, task
from locust.env import Environment
from orjson import JSONDecodeError
from websocket import WebSocket, WebSocketConnectionClosedException, create_connection

from chainbench.util.jsonrpc import RpcCall


class WSSubscription:
    def __init__(self, subscribe_method: str, subscribe_params: dict | list, unsubscribe_method: str):
        self.subscribe_rpc_call: RpcCall = RpcCall(subscribe_method, subscribe_params)
        self.unsubscribe_method: str = unsubscribe_method
        self.subscribed: bool = False
        self._subscription_id: int | str | None = None

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value: int | str):
        self._subscription_id = value
        self.subscribed = True

    @subscription_id.deleter
    def subscription_id(self):
        self._subscription_id = None
        self.subscribed = False


class WSRequest:
    def __init__(self, rpc_call: RpcCall, start_time: int, subscription_index: int | None = None):
        self.rpc_call = rpc_call
        self.start_time = start_time
        self.subscription_index = subscription_index


class WssJrpcUser(User):
    abstract = True
    logger = logging.getLogger(__name__)

    # To be populated by subclass
    subscriptions: list[WSSubscription] = []
    subscription_ids_to_index: dict[str | int, int] = {}

    def __init__(self, environment: Environment):
        super().__init__(environment)
        self._ws: WebSocket | None = None
        self._ws_greenlet: Greenlet | None = None
        self._requests: dict[int, WSRequest] = {}
        self._running: bool = False

    def get_subscription(self, subscription_id: str | int):
        return self.subscriptions[self.subscription_ids_to_index[subscription_id]]

    @task
    def dummy_task(self):
        gevent.sleep(3600)

    def on_start(self) -> None:
        self._running = True
        host: str = self.environment.parsed_options.host
        if host.startswith("ws") or host.startswith("wss"):
            self.connect(host)
        else:
            raise ValueError("Invalid host provided. Expected ws or wss protocol")
        self.subscribe_all()

    def on_stop(self) -> None:
        self.unsubscribe_all()
        timeout = Timeout(30)
        timeout.start()
        try:
            while self._requests:
                gevent.sleep(1)
        except Timeout:
            self.logger.error("Timeout 30s - Failed to unsubscribe from all subscriptions")
        timeout.close()
        self._running = False
        self.logger.debug("Unsubscribed from all subscriptions")

    def connect(self, host: str):
        self._ws = create_connection(host, skip_utf8_validation=True)
        self._ws_greenlet = gevent.spawn(self.receive_loop)

    def subscribe_all(self):
        for i in range(len(self.subscriptions)):
            self.subscribe(self.subscriptions[i], i)

    def subscribe(self, subscription: WSSubscription, index: int):
        self.send(rpc_call=subscription.subscribe_rpc_call, subscription_index=index)

    def unsubscribe_all(self):
        for i in range(len(self.subscriptions)):
            self.unsubscribe(self.subscriptions[i], i)

    def unsubscribe(self, subscription: WSSubscription, index: int):
        params = [subscription.subscription_id]
        self.send(method=subscription.unsubscribe_method, params=params, subscription_index=index)

    def get_notification_name(self, parsed_response: dict):
        # Override this method to return the name of the notification if this is not correct
        return parsed_response["method"]

    def on_message(self, message: str | bytes):
        try:
            parsed_json: dict = json.loads(message)
            if "error" in parsed_json:
                self.environment.events.request.fire(
                    request_type="WSJrpcErr",
                    name=f"JsonRPC Error {parsed_json['error']['code']}",
                    response_time=None,
                    response_length=len(message),
                    exception=None,
                    response=message,
                )
                return
            if "id" not in parsed_json:
                self.environment.events.request.fire(
                    request_type="WSNotif",
                    name=self.get_notification_name(parsed_json),
                    response_time=None,
                    response_length=len(message),
                    exception=None,
                )
                return
            if request := self.get_request(parsed_json):
                if request.subscription_index is not None:
                    self.subscriptions[request.subscription_index].subscription_id = parsed_json["result"]
                    self.subscriptions[request.subscription_index].subscribed = "subscribed"
                    self.subscription_ids_to_index.update({parsed_json["result"]: request.subscription_index})
                self.environment.events.request.fire(
                    request_type="WSJrpc",
                    name=request.rpc_call.method,
                    response_time=((time.time_ns() - request.start_time) / 1_000_000).__round__(),
                    response_length=len(message),
                    exception=None,
                )
            else:
                self.logger.error("Received message with unknown id")
        except JSONDecodeError:
            self.environment.events.request.fire(
                request_type="WSErr",
                name="JSONDecodeError",
                response_time=None,
                response_length=len(message),
                exception=JSONDecodeError,
                response=message,
            )

    def get_request(self, json_response: dict):
        if json_response["id"] not in self._requests:
            self.logger.error("Received message with unknown id")
            self.logger.error(json_response)
            return None
        return self._requests.pop(json_response["id"])

    def receive_loop(self):
        try:
            while self._running:
                message = self._ws.recv()
                self.logger.debug(f"WSResp: {message.strip()}")
                self.on_message(message)
            else:
                self._ws.close()
        except WebSocketConnectionClosedException:
            self.environment.events.request.fire(
                request_type="WSerr",
                name="WebSocket Connection",
                response_time=None,
                response_length=0,
                exception=WebSocketConnectionClosedException,
            )
            self._running = False
            self.logger.error("Connection closed by server, trying to reconnect...")
            self.on_start()

    def send(
        self,
        rpc_call: RpcCall | None = None,
        method: str | None = None,
        params: dict | list | None = None,
        subscription_index: int | None = None,
    ):
        def _get_args():
            if rpc_call:
                return rpc_call
            elif method:
                return RpcCall(method, params)
            else:
                raise ValueError("Either rpc_call or method must be provided")

        rpc_call = _get_args()
        self.logger.debug(f"Sending: {rpc_call or method}")

        if rpc_call is None:
            raise ValueError("Either rpc_call or method must be provided")

        if rpc_call is None and (method is not None):
            rpc_call = RpcCall(method, params)
        elif rpc_call is None and (method is None):
            raise ValueError("Either rpc_call or method must be provided")
        self._requests.update(
            {rpc_call.request_id: WSRequest(rpc_call, start_time=time.time_ns(), subscription_index=subscription_index)}
        )
        json_body = json.dumps(rpc_call.request_body())
        self.logger.debug(f"WSReq: {json_body.decode('utf-8')}")
        if self._ws:
            self._ws.send(json_body)

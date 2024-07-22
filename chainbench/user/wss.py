import json
import logging
import time

import websocket
import gevent
from locust import User
from websocket import WebSocket


class WssUser(User):
    abstract = True

    def __init__(self, environment):
        super().__init__(environment)
        self.ws: WebSocket | None = None
        self.ws_greenlet = None
        self.start_time = None
        self.name = None

    def on_start(self) -> None:
        self.connect(self.environment.parsed_options.host)

    def on_stop(self) -> None:
        self.ws_greenlet.kill()
        self.ws.close()

    def connect(self, host: str, **kwargs):
        self.ws = websocket.create_connection(host, **kwargs)
        self.ws_greenlet = gevent.spawn(self.receive_loop)

    def on_message(self, message):  # override this method in your subclass for custom handling
        response_time = ((time.time_ns() - self.start_time) / 1_000_000).__round__()
        self.environment.events.request.fire(
            request_type="WSR",
            name=self.name,
            response_time=response_time,
            response_length=len(message),
            exception=None,
        )

    def receive_loop(self):
        while True:
            message = self.ws.recv()
            logging.debug(f"WSR: {message}")
            self.on_message(message)

    def send(self, body, name):
        json_body = json.dumps(body)
        logging.debug(f"WSS: {json_body}")
        self.start_time = time.time_ns()
        self.name = name
        self.ws.send(json_body)

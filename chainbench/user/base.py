import logging
import typing as t

from locust import FastHttpUser, between
from locust.contrib.fasthttp import RestResponseContextManager
from locust.exception import RescheduleTask

from chainbench.test_data import BaseTestData, DummyTestData
from chainbench.util.event import setup_event_listeners
from chainbench.util.rpc import generate_request

setup_event_listeners()


class BaseBenchUser(FastHttpUser):
    """Base class for all benchmark users."""

    abstract = True
    wait_time = between(0, 2)

    rpc_path: str = ""

    connection_timeout = 120
    network_timeout = 360

    test_data: BaseTestData = DummyTestData()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def on_start(self):
        self.test_data.wait()

    def on_stop(self):
        self.test_data.close()

    def check_fatal(self, response: RestResponseContextManager):
        if response.status_code == 401:
            self.logger.critical(f"⛔️ Unauthorized request to {response.url}")
        elif response.status_code == 404:
            self.logger.critical(f"⛔️ Not found: {response.url}")
        elif 500 <= response.status_code <= 599:
            self.logger.critical(
                f"⛔️ Got internal server error when requesting {response.url}"
            )
        elif 300 <= response.status_code <= 399:
            self.logger.critical(f"⛔️ Redirect error: {response.url}")

    def check_response(self, response: RestResponseContextManager):
        """Check the response for errors."""
        if response.status_code != 200:
            self.logger.info(f"Request failed with {response.status_code} code")
            self.logger.debug(
                f"Request to {response.url} failed with {response.status_code} code: {response.text}"  # noqa: E501
            )
            self.check_fatal(response)
            response.failure(f"Request failed with {response.status_code} code")
            response.raise_for_status()

        if response.request:
            self.logger.debug(f"Request: {response.request.body}")

        if response.js is None:
            self.logger.error(f"Response is not a JSON: {response.text}")
            response.failure("Response is not a JSON")
            raise RescheduleTask()

        if "jsonrpc" not in response.js:
            self.logger.error(f"Response is not a JSON-RPC: {response.text}")
            response.failure("Response is not a JSON-RPC")
            raise RescheduleTask()

        if "error" in response.js:
            self.logger.error(f"Response has a JSON-RPC error: {response.text}")
            if "code" in response.js["error"]:
                response.failure(
                    f"Response has a JSON-RPC error {response.js['error']['code']}"
                )
                raise RescheduleTask()
            response.failure("Unspecified JSON-RPC error")
            raise RescheduleTask()

        if not response.js.get("result"):
            self.logger.error(f"No result in response: {response.text}")

    def make_call(self, name: str, method: str, params: list[t.Any] | None = None):
        return self._post(name, data=generate_request(method, params))

    def _post(self, name: str, data: t.Optional[dict] = None):
        """Make a JSON-RPC call."""
        with self.rest("POST", self.rpc_path, json=data, name=name) as response:
            self.check_response(response)

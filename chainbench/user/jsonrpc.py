import logging
import typing as t

from locust import FastHttpUser
from locust.contrib.fasthttp import RestResponseContextManager

from chainbench.test_data import TestData
from chainbench.util.rng import RNGManager
from chainbench.util.rpc import generate_request

# importing plugins here as all profiles depend on it
import locust_plugins  # isort: skip  # noqa


class JsonRPCUser(FastHttpUser):
    """Extension of FastHttpUser to provide JsonRPC support."""

    abstract = True
    test_data: TestData = TestData()

    rpc_path: str = ""
    rpc_error_code_exclusions: list[int] = []

    connection_timeout = 120
    network_timeout = 360

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.rng = RNGManager()

    def on_start(self) -> None:
        self.test_data.wait()

    def on_stop(self) -> None:
        self.test_data.close()

    @classmethod
    def get_method(cls, method: str) -> t.Callable:
        return getattr(cls, method)

    def check_fatal(self, response: RestResponseContextManager) -> None:
        if response.status_code == 401:
            self.logger.critical(f"Unauthorized request to {response.url}")
        elif response.status_code == 404:
            self.logger.critical(f"Not found: {response.url}")
        elif 500 <= response.status_code <= 599:
            self.logger.critical(f"Got internal server error when requesting {response.url}")
        elif 300 <= response.status_code <= 399:
            self.logger.critical(f"Redirect error: {response.url}")

    def check_response(self, response: RestResponseContextManager, name: str) -> None:
        response_json: dict = response.js

        if response.request:
            self.logger.debug(f"Request: {response.request.body}")

        """Check the response for errors."""
        if response.status_code != 200:
            self.logger.info(f"Request failed with {response.status_code} code")
            self.logger.debug(
                f"Request to {response.url} failed with HTTP Error {response.status_code} code: {response.text}"
            )
            self.check_fatal(response)
            response.failure(f"Request failed with {response.status_code} code")
            return

        if response_json is None:
            self.logger.error(f"Response for {name}  is not a JSON: {response.text}")
            response.failure(f"Response for {name}  is not a JSON")
            return

        if "jsonrpc" not in response_json:
            self.logger.error(f"Response for {name} is not a JSON-RPC: {response.text}")
            response.failure(f"Response for {name} is not a JSON-RPC")
            return

        if "error" in response_json:
            self.logger.error(f"Response for {name} has a JSON-RPC error: {response.text}")
            if "code" in response_json["error"]:
                if response_json["error"]["code"] not in self.rpc_error_code_exclusions:
                    response.failure(
                        f"Response for {name} has a JSON-RPC error {response_json['error']['code']} - "
                        f"{response_json['error']['message']}"
                    )
            else:
                response.failure("Unspecified JSON-RPC error")
            return

        if not response_json.get("result"):
            self.logger.error(f"Response for {name} call has no result: {response.text}")

    def make_call(
        self, method: str, params: list[t.Any] | dict | None = None, name: str | None = None, url_postfix: str = ""
    ) -> None:
        """Make a JSON-RPC call."""
        name = name if name else method
        return self._post(name, data=generate_request(method, params), url_postfix=url_postfix)

    def _post(self, name: str, data: t.Optional[dict] = None, url_postfix: str = "") -> None:
        with self.rest("POST", self.rpc_path + url_postfix, json=data, name=name) as response:
            self.check_response(response, name=name)

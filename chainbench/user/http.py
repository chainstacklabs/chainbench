import logging
import typing as t

from locust import FastHttpUser
from locust.contrib.fasthttp import RestResponseContextManager

from chainbench.test_data import TestData
from chainbench.util.rng import RNGManager
from chainbench.util.rpc import generate_request


class HttpUser(FastHttpUser):
    """Extension of FastHttpUser for Chainbench."""

    abstract = True
    test_data: TestData = TestData()
    logger = logging.getLogger(__name__)
    rng = RNGManager()

    connection_timeout = 120
    network_timeout = 360

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

    def is_http_error(self, response: RestResponseContextManager) -> bool:
        if response.request is not None:
            self.logger.debug(f"Request: {response.request.method} {response.request.url_split}")
            if response.request.body is not None:
                self.logger.debug(f"{response.request.body}")

        """Check the response for errors."""
        if response.status_code != 200:
            self.logger.info(f"Request failed with {response.status_code} code")
            self.logger.debug(
                f"Request to {response.url} failed with HTTP Error {response.status_code} code: {response.text}"
            )
            self.check_fatal(response)
            response.failure(f"Request failed with {response.status_code} code")
            return True
        return False

    def is_json(self, response: RestResponseContextManager, name: str) -> bool:
        if response.js is None:
            self.logger.error(f"Response for {name}  is not a JSON: {response.text}")
            response.failure(f"Response for {name}  is not a JSON")
            return False
        return True

    def post(
        self, name: str, data: t.Optional[dict] = None, params: t.Optional[dict] = None, url_postfix: str = ""
    ) -> RestResponseContextManager | None:
        with self.rest("POST", url_postfix.strip("/"), json=data, params=params, name=name) as response:
            if self.is_http_error(response):
                return None
            return response

    def get(
        self, name: str, params: t.Optional[dict] = None, url_postfix: str = ""
    ) -> RestResponseContextManager | None:
        with self.rest("GET", url_postfix.strip("/"), params=params, name=name) as response:
            if self.is_http_error(response):
                return None
            return response


class JsonRpcUser(HttpUser):
    """Extension of HttpUser to provide JsonRPC support."""

    rpc_path = ""
    rpc_error_code_exclusions: list[int] = []

    def check_json_rpc_response(self, response: RestResponseContextManager, name: str) -> None:
        if "jsonrpc" not in response.js:
            self.logger.error(f"Response for {name} is not a JSON-RPC: {response.text}")
            response.failure(f"Response for {name} is not a JSON-RPC")
            return

        if "error" in response.js:
            self.logger.error(f"Response for {name} has a JSON-RPC error: {response.text}")
            if "code" in response.js["error"]:
                if response.js["error"]["code"] not in self.rpc_error_code_exclusions:
                    response.failure(
                        f"Response for {name} has a JSON-RPC error {response.js['error']['code']} - "
                        f"{response.js['error']['message']}"
                    )
            else:
                response.failure("Unspecified JSON-RPC error")
            return

        if not response.js.get("result"):
            self.logger.error(f"Response for {name} call has no result: {response.text}")

    def make_rpc_call(
        self, method: str, params: list[t.Any] | dict | None = None, name: str | None = None, url_postfix: str = ""
    ) -> None:
        """Make a JSON-RPC call."""
        name = name if name else method

        response = self.post(name, data=generate_request(method, params), url_postfix=self.rpc_path + url_postfix)
        if response is not None:
            if self.is_json(response, name=name):
                self.check_json_rpc_response(response, name=name)

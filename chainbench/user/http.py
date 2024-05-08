import json
import logging
import random
import typing as t

from locust import FastHttpUser
from locust.contrib.fasthttp import ResponseContextManager

from chainbench.test_data import TestData
from chainbench.util.rng import RNGManager


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

    def check_fatal(self, response: ResponseContextManager) -> None:
        if response.status_code == 401:
            self.logger.critical(f"Unauthorized request to {response.url}")
        elif response.status_code == 404:
            self.logger.critical(f"Not found: {response.url}")
        elif 500 <= response.status_code <= 599:
            self.logger.critical(f"Got internal server error when requesting {response.url}")
        elif 300 <= response.status_code <= 399:
            self.logger.critical(f"Redirect error: {response.url}")

    def check_http_error(self, response: ResponseContextManager) -> None:
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
            response.raise_for_status()

    def post(
        self, name: str, data: t.Optional[dict] = None, params: t.Optional[dict] = None, path: str = ""
    ) -> ResponseContextManager:
        with self.client.request("POST", path, json=data, params=params, name=name, catch_response=True) as response:
            self.check_http_error(response)
            return response

    def get(self, name: str, params: t.Optional[dict] = None, path: str = "") -> ResponseContextManager:
        with self.client.request("GET", path, params=params, name=name, catch_response=True) as response:
            self.check_http_error(response)
            return response


class RpcCall:
    def __init__(self, method: str, params: list[t.Any] | dict | None = None) -> None:
        self.method = method
        self.params = params


class JsonRpcUser(HttpUser):
    """Extension of HttpUser to provide JsonRPC support."""

    rpc_path = ""
    rpc_error_code_exclusions: list[int] = []

    def check_json_rpc_response(self, response: ResponseContextManager, name: str) -> None:
        CHUNK_SIZE = 1024
        if response.text is None:
            self.logger.error(f"Response for {name} is empty")
            response.failure(f"Response for {name} is empty")
            return
        data = response.text[:CHUNK_SIZE]
        if "jsonrpc" not in data:
            self.logger.error(f"Response for {name} is not a JSON-RPC: {response.text}")
            response.failure(f"Response for {name} is not a JSON-RPC")
            return

        if "error" in data:
            response_js = response.json()
            if "error" in response_js:
                if "code" in response_js["error"]:
                    self.logger.error(f"Response for {name} has a JSON-RPC error: {response.text}")
                    if response_js["error"]["code"] not in self.rpc_error_code_exclusions:
                        response.failure(
                            f"Response for {name} has a JSON-RPC error {response_js['error']['code']} - "
                            f"{response_js['error']['message']}"
                        )
                else:
                    response.failure("Unspecified JSON-RPC error")
                return

        if "result" not in data:
            self.logger.error(f"Response for {name} call has no result: {response.text}")

    def make_rpc_call(
        self,
        rpc_call: RpcCall | None = None,
        method: str | None = None,
        params: list[t.Any] | dict | None = None,
        name: str = "",
        path: str = "",
    ) -> None:
        """Make a JSON-RPC call."""
        if rpc_call is not None:
            method = rpc_call.method
            params = rpc_call.params

        if name == "" and method is not None:
            name = method

        with self.client.request(
            "POST", self.rpc_path + path, json=generate_request_body(method, params), name=name, catch_response=True
        ) as response:
            self.check_http_error(response)
            self.check_json_rpc_response(response, name=name)

    def make_batch_rpc_call(self, rpc_calls: list[RpcCall], name: str = "", path: str = "") -> None:
        """Make a Batch JSON-RPC call."""

        if name == "":
            name = "Batch RPC"

        headers = {"Content-Type": "application/json", "accept": "application/json"}

        with self.client.request(
            "POST",
            self.rpc_path + path,
            data=generate_batch_request_body(rpc_calls),
            name=name,
            catch_response=True,
            headers=headers,
        ) as response:
            self.check_http_error(response)
            self.check_json_rpc_response(response, name=name)


def generate_request_body(method: str | None = None, params: list | dict | None = None, version: str = "2.0") -> dict:
    """Generate a JSON-RPC request body."""

    if params is None:
        params = []

    return {
        "jsonrpc": version,
        "method": method,
        "params": params,
        "id": random.randint(1, 100000000),
    }


def generate_batch_request_body(rpc_calls: list[RpcCall], version: str = "2.0") -> str:
    """Generate a batch JSON-RPC request body."""
    return json.dumps(
        [generate_request_body(rpc_call.method, rpc_call.params, version=version) for rpc_call in rpc_calls]
    )

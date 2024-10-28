import logging
import random
import typing as t

from locust import tag, task
from locust.contrib.fasthttp import ResponseContextManager

from chainbench.user.http import HttpUser
from chainbench.util.jsonrpc import (
    RpcCall,
    expand_rpc_calls,
    generate_batch_request_body,
)


class JrpcHttpUser(HttpUser):
    """Extension of HttpUser to provide JsonRPC support."""

    abstract = True
    rpc_path = ""
    rpc_error_code_exclusions: list[int] = []
    rpc_calls: dict[t.Callable, int] = {}  # To be populated in the subclass load profile
    calls_per_batch = 10  # default requests to include in a batch request

    def __init__(self, environment: t.Any):
        self.calls_per_batch = environment.parsed_options.batch_size
        super().__init__(environment)

    @tag("single")
    @task
    def rpc_call_task(self) -> None:
        self.method_to_task_function(self.environment.parsed_options.method)(self)

    @tag("batch")
    @task
    def batch_rpc_call_task(self) -> None:
        rpc_calls = {getattr(self, method.__name__): weight for method, weight in self.rpc_calls.items()}
        self.make_random_batch_rpc_call(
            rpc_calls,
            calls_per_batch=self.calls_per_batch,
        )

    @tag("batch_single")
    @task
    def batch_single_rpc_call_task(self) -> None:
        rpc_call: RpcCall = self.method_to_rpc_call(self.environment.parsed_options.method)(self)
        rpc_calls = [rpc_call for _ in range(self.calls_per_batch)]
        self.make_batch_rpc_call(
            rpc_calls,
        )

    @classmethod
    def method_to_rpc_call(cls, method: str) -> t.Callable:
        method_name = cls.method_to_function_name(method)
        return getattr(cls, method_name)

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
            response_js: list | dict = response.json()
            if isinstance(response_js, dict):
                response_js = [response_js]
            if isinstance(response_js, list):
                for response_js_item in response_js:
                    if "error" in response_js_item:
                        if "code" in response_js_item["error"]:
                            self.logger.error(f"Response for {name} has a JSON-RPC error: {response.text}")
                            if response_js_item["error"]["code"] not in self.rpc_error_code_exclusions:
                                response.failure(
                                    f"Response for {name} has a JSON-RPC error {response_js_item['error']['code']} - "
                                    f"{response_js_item['error']['message']}"
                                )
                                return
                        response.failure("Unspecified JSON-RPC error")
                        self.logger.error(f"Unspecified JSON-RPC error: {response.text}")
                        return
            # TODO: handle multiple errors in batch response properly

        if "result" not in data:
            response.failure(f"Response for {name} call has no result")
            self.logger.error(f"Response for {name} call has no result: {response.text}")

    def make_rpc_call(
        self,
        rpc_call: RpcCall | None = None,
        method: str | None = None,
        params: list[t.Any] | dict | None = None,
        name: str | None = None,
        path: str = "",
    ) -> None:
        """Make a JSON-RPC call."""
        if rpc_call is None:
            if method is None:
                raise ValueError("Either rpc_call or method must be provided")
            else:
                rpc_call = RpcCall(method, params)
        if name is None:
            name = rpc_call.method

        with self.client.request(
            "POST", self.rpc_path + path, json=rpc_call.request_body(), name=name, catch_response=True
        ) as response:
            self.check_http_error(response)
            self.check_json_rpc_response(response, name=name)
            if logging.getLogger("locust").level == logging.DEBUG:
                self.logger.debug(f"jsonrpc: {rpc_call.method} - params: {rpc_call.params}, response: {response.text}")
            else:
                self.logger.info(f"jsonrpc: {rpc_call.method} - params: {rpc_call.params}")

    def make_batch_rpc_call(self, rpc_calls: list[RpcCall], name: str = "", path: str = "") -> None:
        """Make a Batch JSON-RPC call."""

        if name == "":
            name = f"Batch RPC ({len(rpc_calls)})"

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

    def make_random_batch_rpc_call(
        self,
        weighted_rpc_calls: dict[t.Callable[[], RpcCall], int],
        calls_per_batch: int,
        name: str = "",
        path: str = "",
    ) -> None:
        """Make a Batch JSON-RPC call."""
        rpc_calls: list[RpcCall] = expand_rpc_calls(weighted_rpc_calls)
        random_rpc_calls: list[RpcCall] = random.choices(rpc_calls, k=calls_per_batch)

        self.make_batch_rpc_call(random_rpc_calls, name=name, path=path)

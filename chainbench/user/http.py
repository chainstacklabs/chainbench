import json
import logging
import random
import typing as t

from locust import FastHttpUser, TaskSet, tag, task
from locust.contrib.fasthttp import ResponseContextManager

from chainbench.test_data import TestData
from chainbench.util.rng import RNGManager


class RpcCall:
    def __init__(self, method: str, params: list[t.Any] | dict | None = None) -> None:
        self.method = method
        self.params = params


def expand_rpc_calls(rpc_calls_weighted: dict[t.Callable[[], RpcCall], int]) -> list[RpcCall]:
    rpc_call_methods_weighted: dict[RpcCall, int] = {}
    for rpc_call_method, weight in rpc_calls_weighted.items():
        rpc_call_methods_weighted[rpc_call_method()] = weight

    expanded_rpc_calls: list[RpcCall] = expand_to_list(rpc_call_methods_weighted)
    return expanded_rpc_calls


def expand_to_list(items_weighted: dict[t.Any, int] | list[t.Any | tuple[t.Any, int]]) -> list[t.Any]:
    expanded_items_list: list[t.Any] = []
    if isinstance(items_weighted, dict):
        items_weighted = list(items_weighted.items())

    if isinstance(items_weighted, list):
        for rpc_call in items_weighted:
            if isinstance(rpc_call, tuple):
                rpc_call, count = rpc_call
                for _ in range(count):
                    expanded_items_list.append(rpc_call)
            else:
                expanded_items_list.append(rpc_call)

    return expanded_items_list


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

    @staticmethod
    def task_to_method(task_name: str) -> str:
        raise NotImplementedError

    @staticmethod
    def method_to_function_name(method: str) -> str:
        raise NotImplementedError

    @classmethod
    def method_to_task_function(cls, method: str) -> t.Callable:
        method_name = cls.method_to_function_name(method)
        if not method_name.endswith("task"):
            method_name = method_name + "_task"
        return getattr(cls, method_name)

    @classmethod
    def expand_tasks(cls, load_profile: dict[t.Callable, int]) -> list[t.Callable | TaskSet]:
        tasks = expand_to_list(
            {cls.method_to_task_function(method.__name__): weight for method, weight in load_profile.items()}
        )

        return tasks

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


class JsonRpcUser(HttpUser):
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


def generate_request_body(
    method: str | None = None, params: list | dict | None = None, request_id: int | None = None, version: str = "2.0"
) -> dict:
    """Generate a JSON-RPC request body."""

    if params is None:
        params = []

    if request_id is None:
        request_id = random.randint(1, 100000000)

    return {
        "jsonrpc": version,
        "method": method,
        "params": params,
        "id": request_id,
    }


def generate_batch_request_body(rpc_calls: list[RpcCall], version: str = "2.0") -> str:
    """Generate a batch JSON-RPC request body."""
    return json.dumps(
        [
            generate_request_body(rpc_calls[i].method, rpc_calls[i].params, request_id=i, version=version)
            for i in range(1, len(rpc_calls))
        ]
    )

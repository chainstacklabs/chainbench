import random
import typing as t

import orjson as json


class RpcCall:
    def __init__(self, method: str, params: list[t.Any] | dict | None = None, request_id: int | None = None) -> None:
        self._request_id = request_id
        self.method = method
        self.params = params

    @property
    def request_id(self) -> int:
        if self._request_id is None:
            self._request_id = random.Random().randint(1, 100000000)
        return self._request_id

    def request_body(self, request_id: int | None = None) -> dict:
        """Generate a JSON-RPC request body."""
        if self.params is None:
            self.params = []

        if type(self.params) is dict:
            self.params = [self.params]

        if request_id:
            self._request_id = request_id

        return {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.params,
            "id": self.request_id,
        }


def generate_batch_request_body(rpc_calls: list[RpcCall]) -> str:
    """Generate a batch JSON-RPC request body."""
    return json.dumps([rpc_calls[i].request_body(i) for i in range(1, len(rpc_calls))]).decode("utf-8")


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

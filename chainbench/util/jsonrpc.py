import random
import typing as t

import orjson as json


class RpcCall:
    def __init__(self, method: str, params: list[t.Any] | dict | None = None) -> None:
        self.method = method
        self.params = params


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


def generate_batch_request_body(rpc_calls: list[RpcCall], version: str = "2.0") -> bytes:
    """Generate a batch JSON-RPC request body."""
    return json.dumps(
        [
            generate_request_body(rpc_calls[i].method, rpc_calls[i].params, request_id=i, version=version)
            for i in range(1, len(rpc_calls))
        ]
    )


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

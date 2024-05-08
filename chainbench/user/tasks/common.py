import typing as t
from dataclasses import dataclass

from locust import TaskSet

from chainbench.user.http import RpcCall


@dataclass(frozen=True)
class ChainbenchTask:
    name: str
    method: t.Callable


def get_subclass_tasks(cls: type) -> list[ChainbenchTask]:
    methods = set(dir(cls))
    unique_subclass_methods = methods.difference(*(dir(base) for base in cls.__bases__))
    return [
        ChainbenchTask(method, getattr(cls, method))
        for method in sorted(unique_subclass_methods)
        if method.endswith("task") and callable(getattr(cls, method))
    ]


def get_subclass_rpc_methods(cls: type) -> list[str]:
    methods = set(dir(cls))
    unique_subclass_methods = methods.difference(*(dir(base) for base in cls.__bases__))
    return [method for method in sorted(unique_subclass_methods) if method.endswith("rpc")]


def expand_tasks(
    tasks: dict[t.Callable | TaskSet, int] | list[t.Callable | TaskSet | tuple[t.Callable | TaskSet, int]]
) -> list[t.Callable | TaskSet]:
    new_tasks: list[t.Callable | TaskSet] = []
    if isinstance(tasks, dict):
        tasks = list(tasks.items())

    if isinstance(tasks, list):
        for task in tasks:
            if isinstance(task, tuple):
                task, count = task
                for _ in range(count):
                    new_tasks.append(task)
            else:
                new_tasks.append(task)

    return new_tasks


def expand_batch_rpc(rpc_calls_weighted: dict[RpcCall, int] | list[RpcCall | tuple[RpcCall, int]]) -> list[RpcCall]:
    expanded_rpc_calls: list[RpcCall] = []
    if isinstance(rpc_calls_weighted, dict):
        rpc_calls_weighted = list(rpc_calls_weighted.items())

    if isinstance(rpc_calls_weighted, list):
        for rpc_call in rpc_calls_weighted:
            if isinstance(rpc_call, tuple):
                rpc_call, count = rpc_call
                for _ in range(count):
                    expanded_rpc_calls.append(rpc_call)
            else:
                expanded_rpc_calls.append(rpc_call)

    return expanded_rpc_calls

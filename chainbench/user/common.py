import os
import sys
import typing as t
from dataclasses import dataclass

from chainbench.user.protocol.ethereum import EthBeaconUser
from chainbench.user.protocol.evm import EvmUser
from chainbench.user.protocol.solana import SolanaUser


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


def get_subclass_methods(cls: type) -> list[str]:
    methods = set(dir(cls))
    unique_subclass_methods = methods.difference(*(dir(base) for base in cls.__bases__))
    return [method for method in sorted(unique_subclass_methods)]


all_method_classes: list[t.Type[EthBeaconUser | EvmUser | SolanaUser]] = [
    EthBeaconUser,
    EvmUser,
    SolanaUser,
]


def _all_methods() -> dict[str, str]:
    method_list = {}
    for method_class in all_method_classes:
        filepath = sys.modules[method_class.__module__].__file__
        for task in get_subclass_tasks(method_class):
            if filepath:
                method_list[method_class.task_to_method(task.name)] = os.path.abspath(filepath)
    return method_list


all_methods = _all_methods()

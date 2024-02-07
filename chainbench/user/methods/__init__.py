import os
import sys
from typing import Type

from .common import get_subclass_functions
from .ethereum import EthBeaconMethods
from .evm import EvmMethods

__all__ = [
    "EthBeaconMethods",
    "EvmMethods",
    "get_subclass_functions",
    "all_method_classes",
    "all_methods",
]


all_method_classes: list[Type[EthBeaconMethods | EvmMethods]] = [
    EthBeaconMethods,
    EvmMethods,
]


def _all_methods() -> dict[str, str]:
    method_list = {}
    for method_class in all_method_classes:
        filepath = sys.modules[method_class.__module__].__file__
        for task in get_subclass_functions(method_class):
            if filepath:
                method_list[method_class.task_to_method(task.name)] = os.path.abspath(filepath)
    return method_list


all_methods = _all_methods()

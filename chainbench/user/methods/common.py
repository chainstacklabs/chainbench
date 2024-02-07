import typing as t
from dataclasses import dataclass


@dataclass(frozen=True)
class ChainbenchTask:
    name: str
    method: t.Callable


def get_subclass_functions(cls: type) -> list[ChainbenchTask]:
    methods = set(dir(cls))
    unique_subclass_methods = methods.difference(*(dir(base) for base in cls.__bases__))
    return [
        ChainbenchTask(method, getattr(cls, method))
        for method in sorted(unique_subclass_methods)
        if method.endswith("task") and callable(getattr(cls, method))
    ]

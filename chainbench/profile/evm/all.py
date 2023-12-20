# """
# EVM profile (all supported methods).
# """

from locust import constant_pacing
from locust.user.users import UserMeta

from chainbench.user.evm import EVMMethods
from chainbench.util.cli import get_subclass_methods


class EVMMethodsMeta(UserMeta):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        new_cls.tasks = [EVMMethods.get_method(method) for method in get_subclass_methods(EVMMethods)]
        return new_cls


class EVMAllProfile(EVMMethods, metaclass=EVMMethodsMeta):
    wait_time = constant_pacing(1)

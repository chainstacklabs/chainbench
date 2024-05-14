from chainbench.user.protocol import EthBeaconUser, EvmUser, SolanaUser, StarkNetUser
from chainbench.util.event import setup_event_listeners

from .common import get_subclass_tasks
from .http import HttpUser, JsonRpcUser

# importing plugins here as all profiles depend on it
import locust_plugins  # isort: skip  # noqa

setup_event_listeners()

__all__ = [
    "EthBeaconUser",
    "EvmUser",
    "HttpUser",
    "JsonRpcUser",
    "SolanaUser",
    "StarkNetUser",
    "get_subclass_tasks",
]

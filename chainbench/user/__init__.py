from chainbench.util.event import setup_event_listeners

from .evm import EvmMethods, EvmUser
from .http import ChainbenchHttpUser, JsonRpcUser
from .solana import SolanaUser
from .starknet import StarkNetUser

# importing plugins here as all profiles depend on it
import locust_plugins  # isort: skip  # noqa

setup_event_listeners()

__all__ = [
    "EvmUser",
    "ChainbenchHttpUser",
    "JsonRpcUser",
    "SolanaUser",
    "StarkNetUser",
    "EvmMethods",
]

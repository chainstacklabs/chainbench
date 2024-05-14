"""
Polygon profile.

Note, that eth_sendRawTransaction is excluded from the test because it requires
building a transaction and signing it.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "eth_call" : 100
    "eth_getTransactionReceipt" : 64
    "eth_chainId" : 20
    "eth_getBlockByNumber" : 17
    "eth_blockNumber" : 16
    "eth_getTransactionByHash" : 11
    "eth_getLogs" : 11
    "Others" : 9
```
"""

from locust import constant_pacing

from chainbench.user import EvmUser


class PolygonGeneral(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 41,
        EvmUser.eth_get_transaction_receipt: 26,
        EvmUser.eth_chain_id: 8,
        EvmUser.eth_get_block_by_number: 7,
        EvmUser.eth_block_number: 6,
        EvmUser.eth_get_logs: 5,
        EvmUser.eth_get_transaction_by_hash: 4,
        EvmUser.eth_get_balance: 2,
        EvmUser.trace_block: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

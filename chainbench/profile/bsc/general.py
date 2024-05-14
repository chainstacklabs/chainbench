"""
Bsc profile.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "eth_call" : 100
    "eth_getTransactionReceipt" : 93
    "eth_getLogs" : 36
    "eth_blockNumber" : 28
    "eth_chainId" : 18
    "eth_getBlockByNumber" : 13
    "Others" : 20
```
"""

from locust import constant_pacing

from chainbench.user import EvmUser


class BscProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 33,
        EvmUser.eth_get_transaction_receipt: 31,
        EvmUser.eth_get_logs: 12,
        EvmUser.eth_block_number: 9,
        EvmUser.eth_chain_id: 6,
        EvmUser.eth_get_block_by_number: 4,
        EvmUser.eth_get_transaction_by_hash: 3,
        EvmUser.eth_get_balance: 2,
        EvmUser.eth_get_block_by_hash: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

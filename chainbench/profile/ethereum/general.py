"""
Ethereum profile.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "eth_call" : 100
    "eth_getTransactionReceipt" : 24
    "eth_blockNumber" : 19
    "eth_getBalance" : 12
    "eth_chainId" : 11
    "eth_getBlockByNumber" : 9
    "eth_getTransactionByHash" : 8
    "Others" : 12
```
"""

from locust import constant_pacing

from chainbench.user import EvmUser


class EthereumProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 259,
        EvmUser.eth_get_transaction_receipt: 62,
        EvmUser.eth_block_number: 49,
        EvmUser.eth_get_balance: 31,
        EvmUser.eth_chain_id: 28,
        EvmUser.eth_get_block_by_number: 23,
        EvmUser.eth_get_transaction_by_hash: 21,
        EvmUser.eth_get_logs: 13,
        EvmUser.trace_transaction: 8,
        EvmUser.web3_client_version: 5,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

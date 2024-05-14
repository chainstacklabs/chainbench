"""
Base profile.
```
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class BaseProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 1051,
        EvmUser.eth_get_transaction_receipt: 967,
        EvmUser.eth_get_block_by_number: 375,
        EvmUser.eth_get_logs: 158,
        EvmUser.eth_chain_id: 150,
        EvmUser.debug_trace_transaction: 116,
        EvmUser.eth_block_number: 114,
        EvmUser.eth_get_block_receipts: 63,
        EvmUser.eth_get_balance: 57,
        EvmUser.eth_get_block_by_hash: 41,
        EvmUser.trace_block: 28,
        EvmUser.web3_client_version: 21,
        EvmUser.eth_get_transaction_count: 15,
        EvmUser.eth_get_code: 9,
        EvmUser.eth_get_transaction_by_hash: 9,
        EvmUser.debug_trace_block_by_hash: 8,
        EvmUser.eth_gas_price: 6,
        EvmUser.eth_estimate_gas: 2,
        EvmUser.debug_trace_block_by_number: 2,
        EvmUser.eth_syncing: 1,
        EvmUser.eth_fee_history: 1,
        EvmUser.eth_max_priority_fee_per_gas: 1,
        EvmUser.net_version: 1,
        EvmUser.debug_trace_call: 1,
        EvmUser.net_listening: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

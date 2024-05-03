"""
Base profile.
```
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class BaseProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_call_task: 1051,
            EvmMethods.eth_get_transaction_receipt_task: 967,
            EvmMethods.eth_get_block_by_number_task: 375,
            EvmMethods.eth_get_logs_task: 158,
            EvmMethods.eth_chain_id_task: 150,
            EvmMethods.debug_trace_transaction_task: 116,
            EvmMethods.eth_block_number_task: 114,
            EvmMethods.eth_get_block_receipts_task: 63,
            EvmMethods.eth_get_balance_task: 57,
            EvmMethods.eth_get_block_by_hash_task: 41,
            EvmMethods.trace_block_task: 28,
            EvmMethods.web3_client_version_task: 21,
            EvmMethods.eth_get_transaction_count_task: 15,
            EvmMethods.eth_get_code_task: 9,
            EvmMethods.eth_get_transaction_by_hash_task: 9,
            EvmMethods.debug_trace_block_by_hash_task: 8,
            EvmMethods.eth_gas_price_task: 6,
            EvmMethods.eth_estimate_gas_task: 2,
            EvmMethods.debug_trace_block_by_number_task: 2,
            EvmMethods.eth_syncing_task: 1,
            EvmMethods.eth_fee_history_task: 1,
            EvmMethods.eth_max_priority_fee_per_gas_task: 1,
            EvmMethods.net_version_task: 1,
            EvmMethods.debug_trace_call_task: 1,
            EvmMethods.net_listening_task: 1,
        }
    )

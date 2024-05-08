"""
Base profile.
```
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class BaseProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_call_task: 1051,
            EvmTasks.eth_get_transaction_receipt_task: 967,
            EvmTasks.eth_get_block_by_number_task: 375,
            EvmTasks.eth_get_logs_task: 158,
            EvmTasks.eth_chain_id_task: 150,
            EvmTasks.debug_trace_transaction_task: 116,
            EvmTasks.eth_block_number_task: 114,
            EvmTasks.eth_get_block_receipts_task: 63,
            EvmTasks.eth_get_balance_task: 57,
            EvmTasks.eth_get_block_by_hash_task: 41,
            EvmTasks.trace_block_task: 28,
            EvmTasks.web3_client_version_task: 21,
            EvmTasks.eth_get_transaction_count_task: 15,
            EvmTasks.eth_get_code_task: 9,
            EvmTasks.eth_get_transaction_by_hash_task: 9,
            EvmTasks.debug_trace_block_by_hash_task: 8,
            EvmTasks.eth_gas_price_task: 6,
            EvmTasks.eth_estimate_gas_task: 2,
            EvmTasks.debug_trace_block_by_number_task: 2,
            EvmTasks.eth_syncing_task: 1,
            EvmTasks.eth_fee_history_task: 1,
            EvmTasks.eth_max_priority_fee_per_gas_task: 1,
            EvmTasks.net_version_task: 1,
            EvmTasks.debug_trace_call_task: 1,
            EvmTasks.net_listening_task: 1,
        }
    )

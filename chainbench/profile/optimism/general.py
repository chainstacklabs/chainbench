"""
Optimism profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class OptimismProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_call_task: 1206,
            EvmTasks.eth_get_block_by_number_task: 1129,
            EvmTasks.eth_get_transaction_receipt_task: 963,
            EvmTasks.eth_get_logs_task: 472,
            EvmTasks.eth_block_number_task: 173,
            EvmTasks.web3_client_version_task: 149,
            EvmTasks.eth_get_code_task: 128,
            EvmTasks.debug_trace_block_by_number_task: 111,
            EvmTasks.eth_chain_id_task: 63,
            EvmTasks.trace_block_task: 54,
            EvmTasks.eth_get_balance_task: 45,
            EvmTasks.eth_get_transaction_count_task: 35,
            EvmTasks.eth_get_block_receipts_task: 23,
            EvmTasks.eth_get_block_by_hash_task: 19,
            EvmTasks.eth_get_transaction_by_hash_task: 15,
            EvmTasks.eth_gas_price_task: 11,
            EvmTasks.debug_trace_block_by_hash_task: 7,
            EvmTasks.eth_estimate_gas_task: 3,
            EvmTasks.eth_syncing_task: 2,
            EvmTasks.eth_fee_history_task: 2,
            EvmTasks.eth_max_priority_fee_per_gas_task: 2,
            EvmTasks.net_version_task: 2,
            EvmTasks.debug_trace_call_task: 1,
            EvmTasks.net_listening_task: 1,
        }
    )

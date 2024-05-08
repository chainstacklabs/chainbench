"""
Optimism Archive profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class OptimismArchiveProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_get_block_by_number_task: 479,
            EvmTasks.eth_get_transaction_receipt_task: 407,
            EvmTasks.eth_chain_id_task: 318,
            EvmTasks.eth_call_task: 271,
            EvmTasks.eth_get_logs_task: 113,
            EvmTasks.eth_block_number_task: 30,
            EvmTasks.eth_get_transaction_count_task: 28,
            EvmTasks.net_version_task: 20,
            EvmTasks.eth_get_block_by_hash_task: 18,
            EvmTasks.eth_estimate_gas_task: 10,
            EvmTasks.eth_get_transaction_by_hash_task: 6,
            EvmTasks.eth_get_code_task: 3,
            EvmTasks.eth_get_block_receipts_task: 3,
            EvmTasks.debug_trace_block_by_hash_task: 2,
            EvmTasks.debug_trace_block_by_number_task: 1,
            EvmTasks.eth_get_balance_task: 1,
            EvmTasks.eth_gas_price_task: 1,
        }
    )

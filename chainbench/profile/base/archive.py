"""
Base Archive profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class BaseArchiveProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_get_transaction_receipt_task: 1015,
            EvmTasks.eth_call_task: 211,
            EvmTasks.eth_get_block_by_number_task: 73,
            EvmTasks.debug_trace_transaction_task: 36,
            EvmTasks.eth_block_number_task: 12,
            EvmTasks.eth_get_transaction_by_hash_task: 9,
            EvmTasks.eth_chain_id_task: 8,
            EvmTasks.eth_get_logs_task: 7,
            EvmTasks.trace_block_task: 6,
            EvmTasks.eth_get_block_by_hash_task: 6,
            EvmTasks.eth_get_balance_task: 4,
            EvmTasks.eth_get_code_task: 2,
            EvmTasks.eth_get_block_receipts_task: 2,
            EvmTasks.debug_trace_block_by_hash_task: 1,
            EvmTasks.debug_trace_block_by_number_task: 1,
            EvmTasks.net_version_task: 1,
            EvmTasks.eth_gas_price_task: 1,
            EvmTasks.eth_max_priority_fee_per_gas_task: 1,
            EvmTasks.net_listening_task: 1,
        }
    )

"""
Ronin profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class RoninProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_get_transaction_receipt_task: 1128,
            EvmTasks.eth_get_transaction_by_hash_task: 439,
            EvmTasks.eth_gas_price_task: 431,
            EvmTasks.eth_get_transaction_count_task: 431,
            EvmTasks.eth_get_balance_task: 429,
            EvmTasks.eth_call_task: 322,
            EvmTasks.eth_get_block_by_number_task: 315,
            EvmTasks.eth_estimate_gas_task: 287,
            EvmTasks.eth_get_code_task: 285,
            EvmTasks.debug_trace_block_by_number_task: 191,
            EvmTasks.net_version_task: 129,
            EvmTasks.eth_get_logs_task: 28,
            EvmTasks.eth_chain_id_task: 19,
            EvmTasks.eth_block_number_task: 10,
            EvmTasks.eth_max_priority_fee_per_gas_task: 1,
            EvmTasks.eth_get_block_by_hash_task: 1,
        }
    )

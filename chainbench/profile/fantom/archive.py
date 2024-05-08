"""
Fantom Archive profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class FantomArchiveProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_get_block_by_number_task: 1025,
            EvmTasks.eth_block_number_task: 319,
            EvmTasks.eth_get_transaction_receipt_task: 305,
            EvmTasks.eth_get_logs_task: 228,
            EvmTasks.eth_call_task: 203,
            EvmTasks.eth_get_block_by_hash_task: 146,
            EvmTasks.eth_syncing_task: 96,
            EvmTasks.net_peer_count_task: 96,
            EvmTasks.eth_chain_id_task: 32,
            EvmTasks.eth_get_transaction_by_hash_task: 9,
            EvmTasks.eth_get_code_task: 5,
            EvmTasks.eth_get_balance_task: 2,
            EvmTasks.eth_gas_price_task: 2,
            EvmTasks.eth_get_transaction_count_task: 1,
        }
    )

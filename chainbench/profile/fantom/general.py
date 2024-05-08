"""
Fantom profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class FantomProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_call_task: 1051,
            EvmTasks.eth_get_block_by_number_task: 636,
            EvmTasks.eth_get_transaction_receipt_task: 349,
            EvmTasks.eth_block_number_task: 182,
            EvmTasks.eth_get_logs_task: 150,
            EvmTasks.eth_chain_id_task: 81,
            EvmTasks.eth_get_balance_task: 38,
            EvmTasks.eth_get_block_by_hash_task: 27,
            EvmTasks.eth_gas_price_task: 20,
            EvmTasks.eth_get_transaction_by_hash_task: 17,
            EvmTasks.web3_client_version_task: 16,
            EvmTasks.eth_syncing_task: 5,
            EvmTasks.net_peer_count_task: 4,
            EvmTasks.eth_get_transaction_count_task: 3,
            EvmTasks.eth_get_code_task: 3,
            EvmTasks.trace_block_task: 1,
            EvmTasks.eth_estimate_gas_task: 1,
            EvmTasks.eth_max_priority_fee_per_gas_task: 1,
            EvmTasks.eth_fee_history_task: 1,
        }
    )

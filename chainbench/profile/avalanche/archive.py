"""
Avalanche Archive profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class AvalancheArchiveProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_call_task: 1474,
            EvmTasks.eth_get_block_by_number_task: 502,
            EvmTasks.eth_get_transaction_receipt_task: 281,
            EvmTasks.eth_get_logs_task: 234,
            EvmTasks.eth_block_number_task: 218,
            EvmTasks.eth_chain_id_task: 102,
            EvmTasks.eth_get_code_task: 81,
            EvmTasks.debug_trace_block_by_number_task: 70,
            EvmTasks.debug_trace_block_by_hash_task: 42,
            EvmTasks.eth_get_block_by_hash_task: 41,
            EvmTasks.eth_syncing_task: 38,
            EvmTasks.eth_estimate_gas_task: 33,
            EvmTasks.debug_trace_call_task: 12,
            EvmTasks.eth_get_transaction_by_hash_task: 12,
            EvmTasks.web3_client_version_task: 7,
            EvmTasks.eth_get_balance_task: 6,
            EvmTasks.eth_get_block_receipts_task: 3,
            EvmTasks.net_version_task: 3,
            EvmTasks.eth_get_transaction_count_task: 1,
            EvmTasks.debug_trace_transaction_task: 1,
            EvmTasks.eth_gas_price_task: 1,
        }
    )

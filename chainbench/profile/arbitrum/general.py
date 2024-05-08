"""
Arbitrum profile.
"""

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import expand_tasks


class ArbitrumProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            EvmTasks.eth_call_task: 1007,
            EvmTasks.eth_get_block_by_number_task: 592,
            EvmTasks.eth_get_logs_task: 397,
            EvmTasks.eth_chain_id_task: 186,
            EvmTasks.eth_get_transaction_receipt_task: 168,
            EvmTasks.eth_block_number_task: 165,
            EvmTasks.eth_get_block_by_hash_task: 61,
            EvmTasks.eth_get_balance_task: 50,
            EvmTasks.debug_trace_transaction_task: 48,
            EvmTasks.eth_estimate_gas_task: 28,
            EvmTasks.eth_gas_price_task: 22,
            EvmTasks.eth_get_transaction_count_task: 17,
            EvmTasks.eth_get_transaction_by_hash_task: 14,
            EvmTasks.eth_get_block_receipts_task: 12,
            EvmTasks.debug_trace_block_by_number_task: 12,
            EvmTasks.eth_get_code_task: 7,
            EvmTasks.eth_max_priority_fee_per_gas_task: 5,
            EvmTasks.web3_client_version_task: 3,
            EvmTasks.debug_trace_block_by_hash_task: 3,
            EvmTasks.net_listening_task: 2,
            EvmTasks.net_version_task: 2,
            EvmTasks.eth_syncing_task: 1,
            EvmTasks.eth_fee_history_task: 1,
            EvmTasks.eth_get_transaction_by_block_hash_and_index_task: 1,
            EvmTasks.debug_trace_call_task: 1,
        }
    )

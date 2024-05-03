"""
Optimism Archive profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class OptimismArchiveProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_get_block_by_number_task: 479,
            EvmMethods.eth_get_transaction_receipt_task: 407,
            EvmMethods.eth_chain_id_task: 318,
            EvmMethods.eth_call_task: 271,
            EvmMethods.eth_get_logs_task: 113,
            EvmMethods.eth_block_number_task: 30,
            EvmMethods.eth_get_transaction_count_task: 28,
            EvmMethods.net_version_task: 20,
            EvmMethods.eth_get_block_by_hash_task: 18,
            EvmMethods.eth_estimate_gas_task: 10,
            EvmMethods.eth_get_transaction_by_hash_task: 6,
            EvmMethods.eth_get_code_task: 3,
            EvmMethods.eth_get_block_receipts_task: 3,
            EvmMethods.debug_trace_block_by_hash_task: 2,
            EvmMethods.debug_trace_block_by_number_task: 1,
            EvmMethods.eth_get_balance_task: 1,
            EvmMethods.eth_gas_price_task: 1,
        }
    )

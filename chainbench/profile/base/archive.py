"""
Base Archive profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class BaseArchiveProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_get_transaction_receipt_task: 1015,
            EvmMethods.eth_call_task: 211,
            EvmMethods.eth_get_block_by_number_task: 73,
            EvmMethods.debug_trace_transaction_task: 36,
            EvmMethods.eth_block_number_task: 12,
            EvmMethods.eth_get_transaction_by_hash_task: 9,
            EvmMethods.eth_chain_id_task: 8,
            EvmMethods.eth_get_logs_task: 7,
            EvmMethods.trace_block_task: 6,
            EvmMethods.eth_get_block_by_hash_task: 6,
            EvmMethods.eth_get_balance_task: 4,
            EvmMethods.eth_get_code_task: 2,
            EvmMethods.eth_get_block_receipts_task: 2,
            EvmMethods.debug_trace_block_by_hash_task: 1,
            EvmMethods.debug_trace_block_by_number_task: 1,
            EvmMethods.net_version_task: 1,
            EvmMethods.eth_gas_price_task: 1,
            EvmMethods.eth_max_priority_fee_per_gas_task: 1,
            EvmMethods.net_listening_task: 1,
        }
    )

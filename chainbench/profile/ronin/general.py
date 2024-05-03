"""
Ronin profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class RoninProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_get_transaction_receipt_task: 1128,
            EvmMethods.eth_get_transaction_by_hash_task: 439,
            EvmMethods.eth_gas_price_task: 431,
            EvmMethods.eth_get_transaction_count_task: 431,
            EvmMethods.eth_get_balance_task: 429,
            EvmMethods.eth_call_task: 322,
            EvmMethods.eth_get_block_by_number_task: 315,
            EvmMethods.eth_estimate_gas_task: 287,
            EvmMethods.eth_get_code_task: 285,
            EvmMethods.debug_trace_block_by_number_task: 191,
            EvmMethods.net_version_task: 129,
            EvmMethods.eth_get_logs_task: 28,
            EvmMethods.eth_chain_id_task: 19,
            EvmMethods.eth_block_number_task: 10,
            EvmMethods.eth_max_priority_fee_per_gas_task: 1,
            EvmMethods.eth_get_block_by_hash_task: 1,
        }
    )

"""
Avalanche profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class AvalancheProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_call_task: 976,
            EvmMethods.eth_get_block_by_number_task: 516,
            EvmMethods.eth_get_logs_task: 404,
            EvmMethods.eth_get_transaction_receipt_task: 223,
            EvmMethods.eth_block_number_task: 174,
            EvmMethods.eth_chain_id_task: 155,
            EvmMethods.eth_get_balance_task: 134,
            EvmMethods.eth_get_transaction_by_hash_task: 70,
            EvmMethods.eth_get_block_by_hash_task: 30,
            EvmMethods.web3_client_version_task: 23,
            EvmMethods.eth_gas_price_task: 15,
            EvmMethods.eth_syncing_task: 14,
            EvmMethods.net_version_task: 7,
            EvmMethods.eth_get_transaction_count_task: 6,
            EvmMethods.eth_get_block_receipts_task: 5,
            EvmMethods.eth_get_code_task: 3,
            EvmMethods.eth_max_priority_fee_per_gas_task: 2,
            EvmMethods.eth_estimate_gas_task: 2,
            EvmMethods.eth_fee_history_task: 2,
            EvmMethods.debug_trace_transaction_task: 2,
            EvmMethods.debug_trace_block_by_number_task: 1,
            EvmMethods.debug_trace_block_by_hash_task: 1,
            EvmMethods.net_listening_task: 1,
        }
    )

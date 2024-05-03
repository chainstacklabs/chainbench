"""
Arbitrum profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class ArbitrumProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_call_task: 1007,
            EvmMethods.eth_get_block_by_number_task: 592,
            EvmMethods.eth_get_logs_task: 397,
            EvmMethods.eth_chain_id_task: 186,
            EvmMethods.eth_get_transaction_receipt_task: 168,
            EvmMethods.eth_block_number_task: 165,
            EvmMethods.eth_get_block_by_hash_task: 61,
            EvmMethods.eth_get_balance_task: 50,
            EvmMethods.debug_trace_transaction_task: 48,
            EvmMethods.eth_estimate_gas_task: 28,
            EvmMethods.eth_gas_price_task: 22,
            EvmMethods.eth_get_transaction_count_task: 17,
            EvmMethods.eth_get_transaction_by_hash_task: 14,
            EvmMethods.eth_get_block_receipts_task: 12,
            EvmMethods.debug_trace_block_by_number_task: 12,
            EvmMethods.eth_get_code_task: 7,
            EvmMethods.eth_max_priority_fee_per_gas_task: 5,
            EvmMethods.web3_client_version_task: 3,
            EvmMethods.debug_trace_block_by_hash_task: 3,
            EvmMethods.net_listening_task: 2,
            EvmMethods.net_version_task: 2,
            EvmMethods.eth_syncing_task: 1,
            EvmMethods.eth_fee_history_task: 1,
            EvmMethods.eth_get_transaction_by_block_hash_and_index_task: 1,
            EvmMethods.debug_trace_call_task: 1,
        }
    )

"""
Avalanche Archive profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class AvalancheArchiveProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_call_task: 1474,
            EvmMethods.eth_get_block_by_number_task: 502,
            EvmMethods.eth_get_transaction_receipt_task: 281,
            EvmMethods.eth_get_logs_task: 234,
            EvmMethods.eth_block_number_task: 218,
            EvmMethods.eth_chain_id_task: 102,
            EvmMethods.eth_get_code_task: 81,
            EvmMethods.debug_trace_block_by_number_task: 70,
            EvmMethods.debug_trace_block_by_hash_task: 42,
            EvmMethods.eth_get_block_by_hash_task: 41,
            EvmMethods.eth_syncing_task: 38,
            EvmMethods.eth_estimate_gas_task: 33,
            EvmMethods.debug_trace_call_task: 12,
            EvmMethods.eth_get_transaction_by_hash_task: 12,
            EvmMethods.web3_client_version_task: 7,
            EvmMethods.eth_get_balance_task: 6,
            EvmMethods.eth_get_block_receipts_task: 3,
            EvmMethods.net_version_task: 3,
            EvmMethods.eth_get_transaction_count_task: 1,
            EvmMethods.debug_trace_transaction_task: 1,
            EvmMethods.eth_gas_price_task: 1,
        }
    )

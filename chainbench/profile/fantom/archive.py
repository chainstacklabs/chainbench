"""
Fantom Archive profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class FantomArchiveProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_get_block_by_number_task: 1025,
            EvmMethods.eth_block_number_task: 319,
            EvmMethods.eth_get_transaction_receipt_task: 305,
            EvmMethods.eth_get_logs_task: 228,
            EvmMethods.eth_call_task: 203,
            EvmMethods.eth_get_block_by_hash_task: 146,
            EvmMethods.eth_syncing_task: 96,
            EvmMethods.net_peer_count_task: 96,
            EvmMethods.eth_chain_id_task: 32,
            EvmMethods.eth_get_transaction_by_hash_task: 9,
            EvmMethods.eth_get_code_task: 5,
            EvmMethods.eth_get_balance_task: 2,
            EvmMethods.eth_gas_price_task: 2,
            EvmMethods.eth_get_transaction_count_task: 1,
        }
    )

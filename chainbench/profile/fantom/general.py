"""
Fantom profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class FantomProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_call_task: 1051,
            EvmMethods.eth_get_block_by_number_task: 636,
            EvmMethods.eth_get_transaction_receipt_task: 349,
            EvmMethods.eth_block_number_task: 182,
            EvmMethods.eth_get_logs_task: 150,
            EvmMethods.eth_chain_id_task: 81,
            EvmMethods.eth_get_balance_task: 38,
            EvmMethods.eth_get_block_by_hash_task: 27,
            EvmMethods.eth_gas_price_task: 20,
            EvmMethods.eth_get_transaction_by_hash_task: 17,
            EvmMethods.web3_client_version_task: 16,
            EvmMethods.eth_syncing_task: 5,
            EvmMethods.net_peer_count_task: 4,
            EvmMethods.eth_get_transaction_count_task: 3,
            EvmMethods.eth_get_code_task: 3,
            EvmMethods.trace_block_task: 1,
            EvmMethods.eth_estimate_gas_task: 1,
            EvmMethods.eth_max_priority_fee_per_gas_task: 1,
            EvmMethods.eth_fee_history_task: 1,
        }
    )

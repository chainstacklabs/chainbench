"""
Optimism profile.
"""

from locust import constant_pacing

from chainbench.user.http import assign_tasks
from chainbench.user.methods import EvmMethods


class OptimismProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = assign_tasks(
        {
            EvmMethods.eth_call_task: 1206,
            EvmMethods.eth_get_block_by_number_task: 1129,
            EvmMethods.eth_get_transaction_receipt_task: 963,
            EvmMethods.eth_get_logs_task: 472,
            EvmMethods.eth_block_number_task: 173,
            EvmMethods.web3_client_version_task: 149,
            EvmMethods.eth_get_code_task: 128,
            EvmMethods.debug_trace_block_by_number_task: 111,
            EvmMethods.eth_chain_id_task: 63,
            EvmMethods.trace_block_task: 54,
            EvmMethods.eth_get_balance_task: 45,
            EvmMethods.eth_get_transaction_count_task: 35,
            EvmMethods.eth_get_block_receipts_task: 23,
            EvmMethods.eth_get_block_by_hash_task: 19,
            EvmMethods.eth_get_transaction_by_hash_task: 15,
            EvmMethods.eth_gas_price_task: 11,
            EvmMethods.debug_trace_block_by_hash_task: 7,
            EvmMethods.eth_estimate_gas_task: 3,
            EvmMethods.eth_syncing_task: 2,
            EvmMethods.eth_fee_history_task: 2,
            EvmMethods.eth_max_priority_fee_per_gas_task: 2,
            EvmMethods.net_version_task: 2,
            EvmMethods.debug_trace_call_task: 1,
            EvmMethods.net_listening_task: 1,
        }
    )

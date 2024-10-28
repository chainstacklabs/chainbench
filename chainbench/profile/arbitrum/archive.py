"""
Arbitrum Archive profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class ArbitrumArchiveProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call_task: 676,
        EvmUser.eth_get_block_by_number_task: 431,
        EvmUser.eth_get_transaction_receipt_task: 365,
        EvmUser.eth_get_logs_task: 201,
        EvmUser.eth_chain_id_task: 178,
        EvmUser.debug_trace_block_by_number_task: 131,
        EvmUser.debug_trace_block_by_hash_task: 116,
        EvmUser.eth_get_block_by_hash_task: 106,
        EvmUser.debug_trace_transaction_task: 105,
        EvmUser.eth_block_number_task: 88,
        EvmUser.eth_get_block_receipts_task: 41,
        EvmUser.debug_trace_call_task: 22,
        EvmUser.eth_get_code_task: 15,
        EvmUser.net_version_task: 10,
        EvmUser.web3_client_version_task: 4,
        EvmUser.eth_get_balance_task: 4,
        EvmUser.eth_get_transaction_count_task: 3,
        EvmUser.eth_get_transaction_by_hash_task: 1,
        EvmUser.eth_gas_price_task: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

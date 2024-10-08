"""
Arbitrum profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class ArbitrumProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 1007,
        EvmUser.eth_get_block_by_number: 592,
        EvmUser.eth_get_logs: 397,
        EvmUser.eth_chain_id: 186,
        EvmUser.eth_get_transaction_receipt: 168,
        EvmUser.eth_block_number: 165,
        EvmUser.eth_get_block_by_hash: 61,
        EvmUser.eth_get_balance: 50,
        EvmUser.debug_trace_transaction: 48,
        EvmUser.eth_estimate_gas: 28,
        EvmUser.eth_gas_price: 22,
        EvmUser.eth_get_transaction_count: 17,
        EvmUser.eth_get_transaction_by_hash: 14,
        EvmUser.eth_get_block_receipts: 12,
        EvmUser.debug_trace_block_by_number: 12,
        EvmUser.eth_get_code: 7,
        EvmUser.eth_max_priority_fee_per_gas: 5,
        EvmUser.web3_client_version: 3,
        EvmUser.debug_trace_block_by_hash: 3,
        EvmUser.net_version: 2,
        EvmUser.eth_syncing: 1,
        EvmUser.eth_fee_history: 1,
        EvmUser.eth_get_transaction_by_block_hash_and_index: 1,
        EvmUser.debug_trace_call: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

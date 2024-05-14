"""
Avalanche Archive profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class AvalancheArchiveProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 1474,
        EvmUser.eth_get_block_by_number: 502,
        EvmUser.eth_get_transaction_receipt: 281,
        EvmUser.eth_get_logs: 234,
        EvmUser.eth_block_number: 218,
        EvmUser.eth_chain_id: 102,
        EvmUser.eth_get_code: 81,
        EvmUser.debug_trace_block_by_number: 70,
        EvmUser.debug_trace_block_by_hash: 42,
        EvmUser.eth_get_block_by_hash: 41,
        EvmUser.eth_syncing: 38,
        EvmUser.eth_estimate_gas: 33,
        EvmUser.debug_trace_call: 12,
        EvmUser.eth_get_transaction_by_hash: 12,
        EvmUser.web3_client_version: 7,
        EvmUser.eth_get_balance: 6,
        EvmUser.eth_get_block_receipts: 3,
        EvmUser.net_version: 3,
        EvmUser.eth_get_transaction_count: 1,
        EvmUser.debug_trace_transaction: 1,
        EvmUser.eth_gas_price: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

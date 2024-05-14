"""
Base Archive profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class BaseArchiveProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_get_transaction_receipt: 1015,
        EvmUser.eth_call: 211,
        EvmUser.eth_get_block_by_number: 73,
        EvmUser.debug_trace_transaction: 36,
        EvmUser.eth_block_number: 12,
        EvmUser.eth_get_transaction_by_hash: 9,
        EvmUser.eth_chain_id: 8,
        EvmUser.eth_get_logs: 7,
        EvmUser.trace_block: 6,
        EvmUser.eth_get_block_by_hash: 6,
        EvmUser.eth_get_balance: 4,
        EvmUser.eth_get_code: 2,
        EvmUser.eth_get_block_receipts: 2,
        EvmUser.debug_trace_block_by_hash: 1,
        EvmUser.debug_trace_block_by_number: 1,
        EvmUser.net_version: 1,
        EvmUser.eth_gas_price: 1,
        EvmUser.eth_max_priority_fee_per_gas: 1,
        EvmUser.net_listening: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

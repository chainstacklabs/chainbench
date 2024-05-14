"""
Optimism Archive profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class OptimismArchiveProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_get_block_by_number: 479,
        EvmUser.eth_get_transaction_receipt: 407,
        EvmUser.eth_chain_id: 318,
        EvmUser.eth_call: 271,
        EvmUser.eth_get_logs: 113,
        EvmUser.eth_block_number: 30,
        EvmUser.eth_get_transaction_count: 28,
        EvmUser.net_version: 20,
        EvmUser.eth_get_block_by_hash: 18,
        EvmUser.eth_estimate_gas: 10,
        EvmUser.eth_get_transaction_by_hash: 6,
        EvmUser.eth_get_code: 3,
        EvmUser.eth_get_block_receipts: 3,
        EvmUser.debug_trace_block_by_hash: 2,
        EvmUser.debug_trace_block_by_number: 1,
        EvmUser.eth_get_balance: 1,
        EvmUser.eth_gas_price: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

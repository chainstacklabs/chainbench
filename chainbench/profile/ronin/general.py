"""
Ronin profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class RoninProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_get_transaction_receipt: 1128,
        EvmUser.eth_get_transaction_by_hash: 439,
        EvmUser.eth_gas_price: 431,
        EvmUser.eth_get_transaction_count: 431,
        EvmUser.eth_get_balance: 429,
        EvmUser.eth_call: 322,
        EvmUser.eth_get_block_by_number: 315,
        EvmUser.eth_estimate_gas: 287,
        EvmUser.eth_get_code: 285,
        EvmUser.debug_trace_block_by_number: 191,
        EvmUser.net_version: 129,
        EvmUser.eth_get_logs: 28,
        EvmUser.eth_chain_id: 19,
        EvmUser.eth_block_number: 10,
        EvmUser.eth_max_priority_fee_per_gas: 1,
        EvmUser.eth_get_block_by_hash: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

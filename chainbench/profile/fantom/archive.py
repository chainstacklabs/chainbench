"""
Fantom Archive profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class FantomArchiveProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_get_block_by_number: 1025,
        EvmUser.eth_block_number: 319,
        EvmUser.eth_get_transaction_receipt: 305,
        EvmUser.eth_get_logs: 228,
        EvmUser.eth_call: 203,
        EvmUser.eth_get_block_by_hash: 146,
        EvmUser.eth_syncing: 96,
        EvmUser.net_peer_count: 96,
        EvmUser.eth_chain_id: 32,
        EvmUser.eth_get_transaction_by_hash: 9,
        EvmUser.eth_get_code: 5,
        EvmUser.eth_get_balance: 2,
        EvmUser.eth_gas_price: 2,
        EvmUser.eth_get_transaction_count: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

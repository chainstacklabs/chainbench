"""
Fantom profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class FantomProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 1051,
        EvmUser.eth_get_block_by_number: 636,
        EvmUser.eth_get_transaction_receipt: 349,
        EvmUser.eth_block_number: 182,
        EvmUser.eth_get_logs: 150,
        EvmUser.eth_chain_id: 81,
        EvmUser.eth_get_balance: 38,
        EvmUser.eth_get_block_by_hash: 27,
        EvmUser.eth_gas_price: 20,
        EvmUser.eth_get_transaction_by_hash: 17,
        EvmUser.web3_client_version: 16,
        EvmUser.eth_syncing: 5,
        EvmUser.net_peer_count: 4,
        EvmUser.eth_get_transaction_count: 3,
        EvmUser.eth_get_code: 3,
        EvmUser.trace_block: 1,
        EvmUser.eth_estimate_gas: 1,
        EvmUser.eth_max_priority_fee_per_gas: 1,
        EvmUser.eth_fee_history: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

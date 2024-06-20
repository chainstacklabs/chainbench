"""
Gnosis Archive profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class GnosisArchiveProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_block_number: 284,
        EvmUser.eth_call: 218,
        EvmUser.eth_get_block_by_number: 120,
        EvmUser.eth_syncing: 81,
        EvmUser.net_peer_count: 79,
        EvmUser.eth_get_transaction_receipt: 47,
        EvmUser.eth_get_logs: 26,
        EvmUser.eth_chain_id: 15,
        EvmUser.eth_get_code: 6,
        EvmUser.web3_client_version: 5,
        EvmUser.eth_fee_history: 5,
        EvmUser.eth_get_transaction_count: 2,
        EvmUser.eth_get_balance: 2,
        EvmUser.eth_get_block_by_hash: 2,
        EvmUser.eth_gas_price: 2,
        EvmUser.eth_estimate_gas: 1,
        EvmUser.eth_get_transaction_by_hash: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

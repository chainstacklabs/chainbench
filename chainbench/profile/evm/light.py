"""
EVM profile (light mode).
"""

from locust import constant_pacing

from chainbench.user import EvmUser


class EvmLightProfile(EvmUser):
    wait_time = constant_pacing(1)

    rpc_calls = {
        EvmUser.eth_get_transaction_receipt: 1,
        EvmUser.eth_block_number: 1,
        EvmUser.eth_get_balance: 1,
        EvmUser.eth_chain_id: 1,
        EvmUser.eth_get_block_by_number: 1,
        EvmUser.eth_get_transaction_by_hash: 1,
        EvmUser.web3_client_version: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

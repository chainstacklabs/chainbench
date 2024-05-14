"""
Avalanche profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class AvalancheProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 976,
        EvmUser.eth_get_block_by_number: 516,
        EvmUser.eth_get_logs: 404,
        EvmUser.eth_get_transaction_receipt: 223,
        EvmUser.eth_block_number: 174,
        EvmUser.eth_chain_id: 155,
        EvmUser.eth_get_balance: 134,
        EvmUser.eth_get_transaction_by_hash: 70,
        EvmUser.eth_get_block_by_hash: 30,
        EvmUser.web3_client_version: 23,
        EvmUser.eth_gas_price: 15,
        EvmUser.eth_syncing: 14,
        EvmUser.net_version: 7,
        EvmUser.eth_get_transaction_count: 6,
        EvmUser.eth_get_block_receipts: 5,
        EvmUser.eth_get_code: 3,
        EvmUser.eth_max_priority_fee_per_gas: 2,
        EvmUser.eth_estimate_gas: 2,
        EvmUser.eth_fee_history: 2,
        EvmUser.debug_trace_transaction: 2,
        EvmUser.debug_trace_block_by_number: 1,
        EvmUser.debug_trace_block_by_hash: 1,
        EvmUser.net_listening: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

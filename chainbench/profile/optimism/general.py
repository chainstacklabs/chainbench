"""
Optimism profile.
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser


class OptimismProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        EvmUser.eth_call: 1206,
        EvmUser.eth_get_block_by_number: 1129,
        EvmUser.eth_get_transaction_receipt: 963,
        EvmUser.eth_get_logs: 472,
        EvmUser.eth_block_number: 173,
        EvmUser.web3_client_version: 149,
        EvmUser.eth_get_code: 128,
        EvmUser.debug_trace_block_by_number: 111,
        EvmUser.eth_chain_id: 63,
        EvmUser.trace_block: 54,
        EvmUser.eth_get_balance: 45,
        EvmUser.eth_get_transaction_count: 35,
        EvmUser.eth_get_block_receipts: 23,
        EvmUser.eth_get_block_by_hash: 19,
        EvmUser.eth_get_transaction_by_hash: 15,
        EvmUser.eth_gas_price: 11,
        EvmUser.debug_trace_block_by_hash: 7,
        EvmUser.eth_estimate_gas: 3,
        EvmUser.eth_syncing: 2,
        EvmUser.eth_fee_history: 2,
        EvmUser.eth_max_priority_fee_per_gas: 2,
        EvmUser.net_version: 2,
        EvmUser.debug_trace_call: 1,
        EvmUser.net_listening: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

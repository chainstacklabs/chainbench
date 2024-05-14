"""
EVM profile (heavy mode).
"""

from locust import constant_pacing

from chainbench.user.protocol.evm import EvmUser
from chainbench.user.tag import clear_tags


class EvmHeavyProfile(EvmUser):
    wait_time = constant_pacing(10)

    rpc_calls = {
        EvmUser.debug_trace_block_by_hash: 1,
        EvmUser.debug_trace_block_by_number: 1,
        EvmUser.debug_trace_call: 1,
        EvmUser.debug_trace_transaction: 1,
        EvmUser.debug_get_raw_receipts: 1,
        EvmUser.eth_get_logs: 1,
        EvmUser.trace_replay_block_transactions: 1,
        EvmUser.trace_replay_transaction: 1,
        EvmUser.trace_transaction: 1,
        EvmUser.trace_block: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

    # Clear locust tags to ignore debug-trace method exclusion
    clear_tags(tasks)

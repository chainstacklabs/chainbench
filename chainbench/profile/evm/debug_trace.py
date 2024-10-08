"""
EVM profile (debug_trace methods).
"""

from locust import constant_pacing

from chainbench.user import EvmUser
from chainbench.user.tag import clear_tags


class EvmDebugTraceProfile(EvmUser):
    wait_time = constant_pacing(10)

    rpc_calls = {
        EvmUser.debug_trace_transaction: 1229,
        EvmUser.trace_transaction: 484,
        EvmUser.trace_block: 143,
        EvmUser.debug_trace_call: 60,
        EvmUser.trace_call_many: 25,
        EvmUser.trace_filter: 17,
        EvmUser.trace_replay_block_transactions: 21,
        EvmUser.trace_replay_transaction: 11,
        EvmUser.debug_trace_block_by_hash: 6,
        EvmUser.debug_trace_block_by_number: 6,
        EvmUser.debug_get_raw_receipts: 1,
        EvmUser.debug_storage_range_at: 1,
        EvmUser.debug_trace_block: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)

    # Clear locust tags to ignore debug-trace method exclusion
    clear_tags(tasks)

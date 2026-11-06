import json
import unittest

from chainbench.util.jsonrpc import RpcCall, generate_batch_request_body


class JsonRpcBatchTests(unittest.TestCase):
    def test_single_call_is_included(self) -> None:
        result = json.loads(generate_batch_request_body([RpcCall("eth_blockNumber")]))

        self.assertEqual(result, [{"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 0}])

    def test_all_calls_preserve_order_params_and_positional_ids(self) -> None:
        calls = [
            RpcCall("eth_blockNumber"),
            RpcCall("eth_getBalance", ["0x123", "latest"]),
            RpcCall("getBlock", [42, {"encoding": "json"}]),
        ]

        result = json.loads(generate_batch_request_body(calls))

        self.assertEqual(len(result), len(calls))
        self.assertEqual([entry["method"] for entry in result], [call.method for call in calls])
        self.assertEqual([entry["params"] for entry in result], [[], ["0x123", "latest"], [42, {"encoding": "json"}]])
        self.assertEqual([entry["id"] for entry in result], [0, 1, 2])

    def test_repeated_call_instances_each_get_a_distinct_id(self) -> None:
        call = RpcCall("eth_chainId", request_id=99)

        result = json.loads(generate_batch_request_body([call, call, call]))

        self.assertEqual([entry["method"] for entry in result], ["eth_chainId"] * 3)
        self.assertEqual([entry["id"] for entry in result], [0, 1, 2])

    def test_explicit_zero_overrides_an_existing_request_id(self) -> None:
        call = RpcCall("eth_chainId", request_id=99)

        self.assertEqual(call.request_body(0)["id"], 0)

    def test_empty_batch_remains_empty(self) -> None:
        self.assertEqual(json.loads(generate_batch_request_body([])), [])


if __name__ == "__main__":
    unittest.main()

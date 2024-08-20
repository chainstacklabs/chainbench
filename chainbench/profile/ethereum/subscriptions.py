from chainbench.user import WssJrpcUser
from chainbench.user.protocol.ethereum import EthSubscribe


class EthSubscriptions(WssJrpcUser):
    subscriptions = [
        EthSubscribe(["newHeads"]),
        # logs subscription for approve method signature
        EthSubscribe(["logs", {"topics": ["0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"]}]),
        EthSubscribe(["newPendingTransactions"]),
    ]

    def get_notification_name(self, parsed_response: dict):
        return self.get_subscription(
            subscription_id=parsed_response["params"]["subscription"]
        ).subscribe_rpc_call.params[0]

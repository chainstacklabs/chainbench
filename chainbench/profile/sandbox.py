from chainbench.user import SolanaUser, WssJrpcUser
from chainbench.user.wss import WSSubscription


# TODO: Update Oasis profile to new format and update tutorial in documentation


class SandboxProfile(WssJrpcUser, SolanaUser):
    # wait_time = constant_pacing(1)

    subscriptions = [
        WSSubscription("blockSubscribe", [
                    "all",
                    {
                        "commitment": "confirmed",
                        "encoding": "jsonParsed",
                        "showRewards": True,
                        "transactionDetails": "full",
                        "maxSupportedTransactionVersion": 0
                    }
                ], "blockUnsubscribe"),
        # WSSubscription("slotSubscribe", [], "slotUnsubscribe")
    ]

  #   subscriptions = [
  #       WSSubscription("eth_subscribe", ["newHeads"], "eth_unsubscribe"),
  #       WSSubscription("eth_subscribe", [
  #   "logs",
  #   {
  #     "address": "0x8320fe7702b96808f7bbc0d4a888ed1468216cfd",
  #     "topics": ["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"]
  #   }
  # ], "eth_unsubscribe"),
  #       WSSubscription("eth_subscribe", ["newPendingTransactions"], "eth_unsubscribe"),
  #       WSSubscription("eth_subscribe", ["syncing"], "eth_unsubscribe"),
  #   ]
  #
  #   def get_notification_name(self, parsed_response: dict):
  #       return self.subscriptions[self.subscription_ids_to_index[parsed_response["params"]["subscription"]]].subscribe_rpc_call.params[0]


    #
    # @task
    # def eth_block_number(self):
    #     self.send(
    #         {
    #             "jsonrpc": "2.0",
    #             "method": "eth_blockNumber",
    #             "params": [],
    #             "id": random.Random().randint(0, 100000000)
    #         },
    #         "eth_blockNumber"
    #     )
    #
    # @task
    # def eth_get_logs(self):
    #     self.send(
    #         {
    #             "jsonrpc": "2.0",
    #             "method": "eth_getLogs",
    #             "params": self._get_logs_params_factory(self.rng.get_rng()),
    #             "id": random.Random().randint(0, 100000000)
    #         },
    #         "eth_getLogs"
    #     )

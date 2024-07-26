import random

from locust import constant_pacing, task

from chainbench.user import WssUser, SolanaUser


# TODO: Update Oasis profile to new format and update tutorial in documentation


class SandboxProfile(WssUser, SolanaUser):
    wait_time = constant_pacing(1)

    @task
    def dummy_task(self):
        pass

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

"""

"""

from locust import constant_pacing, task

from chainbench.user.evm import EVMBenchUser
from chainbench.util.rng import get_rng


class GetLogsProfile(EVMBenchUser):
    wait_time = constant_pacing(10)

    @task
    def get_logs_task(self):
        self.make_call(
            name="get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(get_rng()),
        ),

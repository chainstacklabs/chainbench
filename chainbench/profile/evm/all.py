# """
# EVM profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user.tasks import EvmTasks
from chainbench.user.tasks.common import get_subclass_tasks


class EvmAllProfile(EvmTasks):
    wait_time = constant_pacing(1)
    tasks = [task.method for task in get_subclass_tasks(EvmTasks)]

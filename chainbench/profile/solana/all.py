# """
# Solana profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user.tasks.common import get_subclass_tasks
from chainbench.user.tasks.solana import SolanaMethods


class SolanaAllProfile(SolanaMethods):
    wait_time = constant_pacing(1)
    tasks = [task.method for task in get_subclass_tasks(SolanaMethods)]

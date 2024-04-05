# """
# Solana profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user.methods.common import get_subclass_functions
from chainbench.user.methods.solana import SolanaMethods


class SolanaAllProfile(SolanaMethods):
    wait_time = constant_pacing(1)
    tasks = [task.method for task in get_subclass_functions(SolanaMethods)]

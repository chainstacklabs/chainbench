import math

from locust import LoadTestShape


class StepLoadShape(LoadTestShape):
    """
    This load shape determines the number of steps by using the total number of users divided by the spawn rate.
    Duration of each step is calculated by dividing the total run time by the number of steps equally.
    """

    use_common_options = True

    def tick(self):
        run_time = self.get_run_time()
        total_run_time = self.runner.environment.parsed_options.run_time

        if run_time < total_run_time:
            step = self.runner.environment.parsed_options.spawn_rate
            users = self.runner.environment.parsed_options.num_users
            no_of_steps = round(users / step)
            step_time = total_run_time / no_of_steps
            user_count = min(step * math.ceil(run_time / step_time), users)
            return user_count, step
        return None

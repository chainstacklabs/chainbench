from locust import LoadTestShape


class SpikeLoadShape(LoadTestShape):
    """
    A step load shape class that has the following shape:
    10% of users start at the beginning for 40% of the test duration, then 100% of users for 20% of the test duration,
    then 10% of users until the end of the test duration.
    """

    use_common_options = True

    def tick(self):
        run_time = self.get_run_time()
        total_run_time = self.runner.environment.parsed_options.run_time
        period_duration = round(total_run_time / 10)
        spike_run_time_start = period_duration * 4
        spike_run_time_end = period_duration * 6

        if run_time < spike_run_time_start:
            user_count = round(self.runner.environment.parsed_options.num_users / 10)
            return user_count, self.runner.environment.parsed_options.spawn_rate
        elif run_time < spike_run_time_end:
            return self.runner.environment.parsed_options.num_users, self.runner.environment.parsed_options.spawn_rate
        elif run_time < total_run_time:
            user_count = round(self.runner.environment.parsed_options.num_users / 10)
            return user_count, self.runner.environment.parsed_options.spawn_rate
        return None

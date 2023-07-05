import logging

from locust import events
from locust.runners import MasterRunner, WorkerRunner

from chainbench.util.timer import Timer

logger = logging.getLogger(__name__)


def on_test_start(environment, **_kwargs):
    # It will be called for any runner (master, worker, local)
    if not isinstance(environment.runner, MasterRunner):
        # Print worker details to the log
        logger.info(
            f"Worker[{environment.runner.worker_index:02d}]: "
            f"The test is started, Environment: {environment.runner}",
        )
        Timer.set_timer(environment.runner.worker_index)
    else:
        # Print master details to the log
        logger.info(
            f"Master: test_start.add_listener: The test is started, "
            f"Environment: {environment.runner}",
        )


# Listener for the test stop event
def on_test_stop(environment, **_kwargs):
    # It will be called for any runner (master, worker, local)
    runner = environment.runner
    if not isinstance(runner, MasterRunner):
        # Print worker details to the log
        logger.info(
            f"Worker[{runner.worker_index:02d}]: Tests completed in "
            f"{Timer.get_time_diff(runner.worker_index):>.3f} seconds"
        )
    else:
        # Print master details to the log
        logger.info("Master: The test is stopped")


# Listener for the init event
def on_init(environment, **_kwargs):
    # It will be called for any runner (master, worker, local)
    logger.debug("init.add_listener: Init is started")
    logger.debug("init.add_listener: Environment: %s", environment.runner)
    logger.debug("init.add_listener: Host: %s", environment.host)

    host_under_test = environment.host or "Default host"

    if isinstance(environment.runner, MasterRunner):
        # Print master details to the log
        logger.info("I'm a master. Running tests for %s", host_under_test)

    if isinstance(environment.runner, WorkerRunner):
        # Print worker details to the log
        logger.info("I'm a worker. Running tests for %s", host_under_test)
        logger.info("Initializing test data...")
        for user in environment.runner.user_classes:
            if not hasattr(user, "test_data"):
                continue

            user.test_data.update(environment.host)
            logger.info("Test data is ready")


def setup_event_listeners():
    events.test_start.add_listener(on_test_start)
    events.test_stop.add_listener(on_test_stop)
    events.init.add_listener(on_init)

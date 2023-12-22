import logging
import traceback

from locust import events
from locust.runners import MasterRunner, WorkerRunner

from chainbench.util.timer import Timer

logger = logging.getLogger(__name__)


def cli_custom_arguments(parser):
    parser.add_argument(
        "--use-recent-blocks",
        type=bool,
        default=False,
        help="Use recent blocks as test data. Default is False.",
        include_in_web_ui=False,
    )
    parser.add_argument(
        "--size",
        type=str,
        default=None,
        help="Set the size of the test data. e.g. --size S",
        include_in_web_ui=False,
    )


def setup_test_data(environment, msg, **kwargs):
    # Fired when the worker receives a message of type 'test_data'
    test_data = msg.data["data"][0]
    worker_index = msg.data["data"][1]

    for user in environment.runner.user_classes:
        if not hasattr(user, "test_data"):
            continue

        user.test_data.init_data_from_json(test_data[type(user.test_data).__name__])
    environment.runner.send_message("acknowledge_data", f"Test data received by worker {worker_index}")
    logger.info("Test Data received from master")


def on_acknowledge(msg, **kwargs):
    # Fired when the master receives a message of type 'acknowledge_data'
    print(msg.data)


# Listener for the init event
def on_init(environment, **_kwargs):
    # It will be called for any runner (master, worker, local)
    logger.debug("init.add_listener: Init is started")
    logger.debug("init.add_listener: Environment: %s", environment.runner)
    logger.debug("init.add_listener: Host: %s", environment.host)

    host_under_test = environment.host or "Default host"

    if not isinstance(environment.runner, MasterRunner):
        # Print worker details to the log
        logger.info("I'm a worker. Running tests for %s", host_under_test)
        environment.runner.register_message("test_data", setup_test_data)

    test_data = {}

    if not isinstance(environment.runner, WorkerRunner):
        # Print master details to the log
        logger.info("I'm a master. Running tests for %s", host_under_test)
        environment.runner.register_message("acknowledge_data", on_acknowledge)
        try:
            for user in environment.runner.user_classes:
                if not hasattr(user, "test_data"):
                    continue
                user_test_data = getattr(user, "test_data")
                test_data_class_name = type(user_test_data).__name__
                if test_data_class_name not in test_data:
                    logger.info(f"Initializing test data for {test_data_class_name}")
                    print(f"Initializing test data for {test_data_class_name}")
                    user_test_data.update(environment.host, environment.parsed_options)
                    test_data[test_data_class_name] = user_test_data.data.to_json()
        except Exception:
            logger.error(f"Failed to update test data: {traceback.format_exc()}. Exiting...")
            print(f"Failed to update test data: {traceback.format_exc()}. Exiting...")
            environment.runner.quit()
            raise exit()
        else:
            logger.info("Test data is ready")
            for i, worker in enumerate(environment.runner.clients):
                environment.runner.send_message("test_data", {"data": (test_data, i)}, worker)
                logger.info(f"Test data is sent to worker {i}")


def on_test_start(environment, **_kwargs):
    # Print master details to the log
    logger.info(
        f"Master: test_start.add_listener: The test is started, " f"Environment: {environment.runner}",
    )

    if not isinstance(environment.runner, MasterRunner):
        # Print worker details to the log
        logger.info(
            f"Worker[{environment.runner.worker_index:02d}]: "
            f"The test is started, Environment: {environment.runner}",
        )
        Timer.set_timer(environment.runner.worker_index)


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


def setup_event_listeners():
    events.init_command_line_parser.add_listener(cli_custom_arguments)
    events.test_start.add_listener(on_test_start)
    events.test_stop.add_listener(on_test_stop)
    events.init.add_listener(on_init)

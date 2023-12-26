import logging
import traceback

from locust import events
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.rpc import Message
from locust.runners import MasterRunner, WorkerRunner

from chainbench.test_data import EVMTestData
from chainbench.util.timer import Timer

logger = logging.getLogger(__name__)


def cli_custom_arguments(parser: LocustArgumentParser):
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


def setup_test_data(environment: Environment, msg: Message, **kwargs):
    # Fired when the worker receives a message of type 'test_data'
    test_data = msg.data["data"][0]
    worker_index = msg.data["data"][1]

    if isinstance(environment.runner, WorkerRunner):
        for user in environment.runner.user_classes:
            if hasattr(user, "test_data"):
                test_data_class_name = type(user.test_data).__name__
                user.test_data.init_data_from_json(test_data[test_data_class_name])
                if isinstance(user.test_data, EVMTestData):
                    chain_id = test_data["chain_id"][test_data_class_name]
                    user.test_data.set_chain_info(chain_id)
            else:
                raise AttributeError(f"{user} class does not have 'test_data' attribute")
        environment.runner.send_message("acknowledge_data", {"data": f"Test data received by worker {worker_index}"})
        logger.info("Test Data received from master")


def on_acknowledge(msg: Message, **kwargs):
    # Fired when the master receives a message of type 'acknowledge_data'
    print(msg.data["data"])


# Listener for the init event
def on_init(environment: Environment, **_kwargs):
    # It will be called for any runner (master, worker, local)
    logger.debug("init.add_listener: Init is started")
    logger.debug("init.add_listener: Environment: %s", environment.runner)
    logger.debug("init.add_listener: Host: %s", environment.host)

    host_under_test = environment.host or "Default host"

    if isinstance(environment.runner, WorkerRunner):
        # Print worker details to the log
        logger.info("I'm a worker. Running tests for %s", host_under_test)
        environment.runner.register_message("test_data", setup_test_data)

    test_data = {}

    if isinstance(environment.runner, MasterRunner):
        # Print master details to the log
        logger.info("I'm a master. Running tests for %s", host_under_test)
        environment.runner.register_message("acknowledge_data", on_acknowledge)

        try:
            for user in environment.runner.user_classes:
                if hasattr(user, "test_data"):
                    user_test_data = getattr(user, "test_data")
                    test_data_class_name = type(user_test_data).__name__
                    if test_data_class_name not in test_data:
                        logger.info(f"Initializing test data for {test_data_class_name}")
                        print(f"Initializing test data for {test_data_class_name}")
                        user_test_data.set_host(environment.host)
                        if isinstance(user.test_data, EVMTestData):
                            chain_id = user_test_data.fetch_chain_id()
                            user_test_data.set_chain_info(chain_id)
                            logger.info(f"Target endpoint network is {user_test_data.chain_info.name}")
                            print(f"Target endpoint network is {user_test_data.chain_info.name}")
                            test_data["chain_id"] = {test_data_class_name: chain_id}
                        user_test_data.update(environment.parsed_options)
                        test_data[test_data_class_name] = user_test_data.data.to_json()
                else:
                    raise AttributeError(f"{user} class does not have 'test_data' attribute")
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
            if environment.web_ui:
                print(f"Web UI started at: " f"http://{environment.runner.master_bind_host}:8089")
                logger.info(f"Web UI started at: " f"http://{environment.runner.master_bind_host}:8089")


def on_test_start(environment: Environment, **_kwargs):
    # Print master details to the log
    logger.info(
        f"Master: test_start.add_listener: The test is started, " f"Environment: {environment.runner}",
    )

    if isinstance(environment.runner, WorkerRunner):
        # Print worker details to the log
        logger.info(
            f"Worker[{environment.runner.worker_index:02d}]: "
            f"The test is started, Environment: {environment.runner}",
        )
        Timer.set_timer(environment.runner.worker_index)


# Listener for the test stop event
def on_test_stop(environment: Environment, **_kwargs):
    # It will be called for any runner (master, worker, local)
    if isinstance(environment.runner, WorkerRunner):
        # Print worker details to the log
        logger.info(
            f"Worker[{environment.runner.worker_index:02d}]: Tests completed in "
            f"{Timer.get_time_diff(environment.runner.worker_index):>.3f} seconds"
        )
    else:
        # Print master details to the log
        logger.info("Master: The test is stopped")


def setup_event_listeners():
    events.init_command_line_parser.add_listener(cli_custom_arguments)
    events.test_start.add_listener(on_test_start)
    events.test_stop.add_listener(on_test_stop)
    events.init.add_listener(on_init)

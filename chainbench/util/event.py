import logging
import time
import traceback
import typing as t

import gevent
from locust import User, events
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.rpc import Message
from locust.runners import STATE_CLEANUP, MasterRunner, WorkerRunner

from chainbench.test_data import Block, EvmTestData, TestData
from chainbench.test_data.evm import ChainId
from chainbench.util.timer import Timer

logger = logging.getLogger(__name__)


def cli_custom_arguments(parser: LocustArgumentParser):
    parser.add_argument(
        "--use-latest-blocks",
        type=bool,
        default=False,
        help="Use latest blocks as test data. Default is False.",
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
    test_data: dict[str, t.Any] = msg.data["data"][0]
    worker_index: int = msg.data["data"][1]

    if isinstance(environment.runner, WorkerRunner):
        for user in environment.runner.user_classes:
            if hasattr(user, "test_data"):
                test_data_class_name: str = type(user.test_data).__name__
                user.test_data.init_data_from_json(test_data[test_data_class_name])
                if isinstance(user.test_data, EvmTestData):
                    chain_id: ChainId = test_data["chain_id"][test_data_class_name]
                    user.test_data.init_network(chain_id)
            else:
                raise AttributeError(f"{user} class does not have 'test_data' attribute")
        environment.runner.send_message("acknowledge_data", {"data": f"Test data received by worker {worker_index}"})
        logger.info("Test Data received from master")


def on_acknowledge(msg: Message, **kwargs):
    # Fired when the master receives a message of type 'acknowledge_data'
    print(msg.data["data"])


def get_block_worker(master_runner: MasterRunner):
    logger.info("Getting blocks in real time.")
    active_users: list[t.Type[User]] = []
    for user in master_runner.user_classes:
        if hasattr(user, "test_data"):
            if user.test_data.initialized:
                active_users.append(user)
        continue

    while master_runner.state not in [STATE_CLEANUP]:
        blocks: dict[str, t.Any] = {}
        for user in active_users:
            if hasattr(user, "test_data"):
                test_data_class_name: str = type(user.test_data).__name__
                if test_data_class_name in blocks:
                    continue
                latest_block_number = user.test_data.fetch_latest_block_number()
                if latest_block_number not in user.test_data.data.block_numbers:
                    block = user.test_data.fetch_block(latest_block_number)
                    user.test_data.data.push_block(block)
                    blocks[test_data_class_name] = block.to_json()
                    print(f"Block {block.block_number} fetched and updated in test data")
        if len(blocks) > 0:
            for i, worker in enumerate(master_runner.clients):
                master_runner.send_message("block_data", {"data": blocks}, worker)
                logger.info(f"Block data is sent to worker {i}")
        time.sleep(1)


def on_receive_block(environment: Environment, msg: Message, **kwargs):
    # Fired when the worker receives a message of type 'block_data'
    blocks: dict[str, t.Any] = msg.data["data"]

    if isinstance(environment.runner, WorkerRunner):
        for user in environment.runner.user_classes:
            if hasattr(user, "test_data"):
                test_data_class_name = type(user.test_data).__name__
                block: Block = user.test_data.get_block_from_data(blocks[test_data_class_name])
                if block.block_number not in user.test_data.data.block_numbers:
                    user.test_data.data.push_block(block)
                    logger.debug(f"Block {block.block_number} received from master and updated in test data")


# Listener for the init event
def on_init(environment: Environment, **_kwargs):
    # It will be called for any runner (master, worker, local)
    logger.debug("init.add_listener: Init is started")
    logger.debug("init.add_listener: Environment: %s", environment.runner)
    logger.debug("init.add_listener: Host: %s", environment.host)

    host_under_test: str = environment.host or "Default host"

    if isinstance(environment.runner, WorkerRunner):
        # Print worker details to the log
        logger.info("I'm a worker. Running tests for %s", host_under_test)
        environment.runner.register_message("test_data", setup_test_data)
        environment.runner.register_message("block_data", on_receive_block)

    test_data: dict[str, t.Any] = {}

    if isinstance(environment.runner, MasterRunner):
        # Print master details to the log
        logger.info("I'm a master. Running tests for %s", host_under_test)
        environment.runner.register_message("acknowledge_data", on_acknowledge)

        print("Waiting for workers to be ready...")
        start_time = time.time()
        while len(environment.runner.clients.ready) < getattr(environment.parsed_options, "expect_workers"):
            if time.time() - start_time > 60:
                print("Timeout: Workers are not ready after 60 seconds. Exiting...")
                logger.error("Timeout: Workers are not ready after 60 seconds. Exiting...")
                environment.runner.quit()
                raise exit(1)
            time.sleep(1)
        try:
            for user in environment.runner.user_classes:
                if not hasattr(user, "test_data"):
                    raise AttributeError(f"{user} class does not have 'test_data' attribute")
                user_test_data: TestData = getattr(user, "test_data")
                test_data_class_name: str = type(user_test_data).__name__
                if test_data_class_name in test_data:
                    continue
                logger.info(f"Initializing test data for {test_data_class_name}")
                print(f"Initializing test data for {test_data_class_name}")
                if environment.host:
                    user_test_data.init_http_client(environment.host)
                if isinstance(user_test_data, EvmTestData):
                    chain_id: ChainId = user_test_data.fetch_chain_id()
                    user_test_data.init_network(chain_id)
                    logger.info(f"Target endpoint network is {user_test_data.network.name}")
                    print(f"Target endpoint network is {user_test_data.network.name}")
                    test_data["chain_id"] = {test_data_class_name: chain_id}
                if environment.parsed_options:
                    user_test_data.init_data_from_blockchain(environment.parsed_options)
                test_data[test_data_class_name] = user_test_data.data.to_json()
        except Exception as e:
            logger.error(f"Failed to update test data: {e.__class__.__name__}: {e}. Exiting...")
            print(f"Failed to update test data:\n     {e.__class__.__name__}: {e}. Exiting...")
            logger.debug(traceback.format_exc())
            environment.runner.quit()
            raise exit(1)
        else:
            logger.info("Test data is ready")
            for i, worker in enumerate(environment.runner.clients):
                environment.runner.send_message("test_data", {"data": (test_data, i)}, worker)
                logger.info(f"Test data is sent to worker {i}")
            if environment.web_ui:
                print(f"Web UI started at: " f"http://{environment.runner.master_bind_host}:8089")
                logger.info(f"Web UI started at: " f"http://{environment.runner.master_bind_host}:8089")
            if getattr(environment.parsed_options, "use_latest_blocks", False):
                gevent.spawn(get_block_worker, environment.runner)


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

import csv
import logging
from datetime import datetime, timedelta
from json import JSONDecodeError
from pathlib import Path
from time import sleep

from locust.util.timespan import parse_timespan

from .http import HttpClient

logger = logging.getLogger(__name__)


def calculate_lag(current_timestamp: datetime, block_timestamp: datetime) -> int:
    """
    Calculate the difference between the time the node under test received the block,
    and the time when the block producer node produced the block, in seconds.
    Sometimes this value is negative due to difference in precision - block timestamp
    is precise to the second, while current_timestamp is precise to microseconds.
    Therefore, we use max function to ensure the lag calculated is minimum 0 and never
    negative.
    """
    return max(int((current_timestamp - block_timestamp).total_seconds()), 0)


def head_lag_monitor(endpoint: str, result_path: Path, duration: str):
    data = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": ["latest", False],
    }
    end_time = datetime.now() + timedelta(seconds=parse_timespan(duration))
    http = HttpClient(endpoint)
    with open(
        file=f"{result_path}/head_lag.csv",
        mode="a",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        logger.info("Start monitoring head lag")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["timestamp", "lag (s)", "block number"])
        while datetime.now() < end_time:
            current_timestamp = datetime.now()
            response = http.post(data=data)
            try:
                block_timestamp = datetime.fromtimestamp(int(response.json["result"]["timestamp"], 0))
                block_number = int(response.json["result"]["number"], 0)
                csv_writer.writerow(
                    [
                        current_timestamp,
                        f"{calculate_lag(current_timestamp, block_timestamp)}",
                        block_number,
                    ]
                )
                logger.info("Written 1 row to head_lag.csv")
                sleep(10)
            except (KeyError, JSONDecodeError):
                logger.error("Error decoding JSON or key not found")
                sleep(1)
    logger.info("Finished monitoring head lag")


monitors = {"head-lag-monitor": head_lag_monitor}

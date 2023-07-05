import csv
import logging
import re
from datetime import datetime, timedelta
from json import JSONDecodeError
from time import sleep

import httpx

logger = logging.getLogger()


def calculate_lag(current_timestamp, block_timestamp):
    """
    Calculate the difference between the time the node under test received the block,
    and the time when the block producer node produced the block, in seconds.
    Sometimes this value is negative due to difference in precision - block timestamp
    is precise to the second, while current_timestamp is precise to microseconds.
    Therefore, we use max function to ensure the lag calculated is minimum 0 and never
    negative.
    """
    return max(int((current_timestamp - block_timestamp).total_seconds()), 0)


def parse_timespan(time_str):
    """
    Parse a string representing a time span and return the number of seconds.
    Valid formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.
    """
    if not time_str:
        raise ValueError("Invalid time span format")

    if re.match(r"^\d+$", time_str):
        # if an int is specified we assume they want seconds
        return int(time_str)

    timespan_regex = re.compile(
        r"((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
    )
    parts = timespan_regex.match(time_str)
    if not parts:
        raise ValueError(
            "Invalid time span format. "
            "Valid formats: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc."
        )
    parts = parts.groupdict()
    time_params = {name: int(value) for name, value in parts.items() if value}
    if not time_params:
        raise ValueError(
            "Invalid time span format. "
            "Valid formats: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc."
        )
    return int(timedelta(**time_params).total_seconds())


def head_lag_monitor(endpoint, result_path, duration):
    data = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": ["latest", False],
    }
    csv_writer_kwargs = {
        "file": f"{result_path}/head_lag.csv",
        "mode": "a",
        "encoding": "utf-8-sig",
        "newline": "",
    }
    end_time = datetime.now() + timedelta(seconds=parse_timespan(duration))
    http = httpx.Client()
    with open(**csv_writer_kwargs) as csv_file:
        logger.info("Start monitoring head lag")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["timestamp", "lag (s)", "block number"])
        while datetime.now() < end_time:
            current_timestamp = datetime.now()
            response = http.post(endpoint, json=data)
            try:
                block_timestamp = datetime.fromtimestamp(
                    int(response.json()["result"]["timestamp"], 0)
                )
                block_number = int(response.json()["result"]["number"], 0)
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

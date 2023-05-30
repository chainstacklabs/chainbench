import csv
import logging
from datetime import datetime
from time import sleep

import requests
from pandas import to_timedelta
from requests import JSONDecodeError

logger = logging.getLogger()


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
    logger.info("Creating head_lag.csv")
    with open(**csv_writer_kwargs) as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["timestamp", "lag (s)", "block number"])
        logger.info("head_lag.csv created")
    end_time = datetime.now() + to_timedelta(duration)

    logger.info("Start monitoring head lag")
    while datetime.now() < end_time:
        current_timestamp = datetime.now().replace(microsecond=0)
        response = requests.post(endpoint, json=data)
        try:
            block_timestamp = datetime.fromtimestamp(
                int(response.json()["result"]["timestamp"], 0)
            )
            block_number = int(response.json()["result"]["number"], 0)
            with open(**csv_writer_kwargs) as csv_file:
                csv_writer = csv.writer(csv_file)
                logger.info("Write row to head_lag.csv")
                csv_writer.writerow(
                    [
                        current_timestamp,
                        f"{max(int((current_timestamp - block_timestamp).total_seconds()), 0)}",  # noqa E501
                        block_number,
                    ]
                )
                logger.info("Written 1 row to head_lag.csv")
        except (KeyError, JSONDecodeError):
            logger.error("Error decoding JSON or key not found")
        sleep(10)


monitors = {"head-lag-monitor": head_lag_monitor}

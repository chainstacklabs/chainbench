import csv
import logging
import typing
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

from locust.util.timespan import parse_timespan
from orjson import JSONDecodeError

from ..user import SolanaUser
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


# EVM
def eth_get_block_by_number(http_client: HttpClient) -> dict:
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getBlockByNumber",
        "params": ["latest", False],
    }
    response = http_client.post(data=body)
    return response.json["result"]


# Solana


def get_slot(http_client: HttpClient) -> int:
    response = http_client.post(data={"jsonrpc": "2.0", "id": 1, "method": "getSlot", "params": []})
    return response.json["result"]


def get_block(http_client: HttpClient, slot: int) -> dict:
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [
            slot,
            {
                "encoding": "jsonParsed",
                "transactionDetails": "none",
                "rewards": False,
                "maxSupportedTransactionVersion": 0,
            },
        ],
    }
    response = http_client.post(data=body)
    return response.json["result"]


def sync_lag_monitor(user_class: typing.Any, endpoint: str, result_path: Path, duration: str):
    end_time = datetime.now() + timedelta(seconds=parse_timespan(duration))
    http = HttpClient(endpoint)
    with open(
        file=f"{result_path}/sync_lag.csv",
        mode="a",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        logger.info("Start monitoring sync lag")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["timestamp", "lag (s)", "block number"])
        while datetime.now() < end_time:
            current_timestamp = datetime.now()
            try:
                if user_class == SolanaUser:
                    block_number = get_slot(http)
                    block = get_block(http, block_number)
                    block_timestamp = datetime.fromtimestamp(block["blockTime"])
                else:
                    block = eth_get_block_by_number(http)
                    block_timestamp = datetime.fromtimestamp(int(block["timestamp"], 0))
                    block_number = int(block["number"], 0)
                csv_writer.writerow(
                    [
                        current_timestamp,
                        f"{calculate_lag(current_timestamp, block_timestamp)}",
                        block_number,
                    ]
                )
                logger.info("Written 1 row to sync_lag.csv")
                sleep(10)
            except (KeyError, JSONDecodeError):
                logger.error("Error decoding JSON or key not found")
                sleep(1)
    logger.info("Finished monitoring sync lag")


monitors = {"sync-lag-monitor": sync_lag_monitor}

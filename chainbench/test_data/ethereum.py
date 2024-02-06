import json
import logging
import typing as t
from argparse import Namespace
from dataclasses import dataclass

from chainbench.test_data.blockchain import (
    Block,
    BlockNotFoundError,
    BlockNumber,
    BlockRange,
    TestData,
)
from chainbench.util.rng import RNG

logger = logging.getLogger(__name__)

Epoch = int


class EthValidatorStatus:
    ACTIVE = "active"
    ACTIVE_ONGOING = "active_ongoing"
    ACTIVE_EXITING = "active_exiting"
    ACTIVE_SLASHED = "active_slashed"
    PENDING = "pending"
    PENDING_ONGOING = "pending_ongoing"
    PENDING_INITIALIZED = "pending_initialized"
    EXITED = "exited"
    EXITED_UNSLASHED = "exited_unslashed"
    EXITED_SLASHED = "exited_slashed"
    WITHDRAWAL = "withdrawal"
    WITHDRAWAL_DONE = "withdrawal_done"
    WITHDRAWAL_POSSIBLE = "withdrawal_possible"


EthValidatorStatuses = [v for k, v in EthValidatorStatus.__dict__.items() if not k.startswith("_")]


@dataclass(frozen=True)
class EthValidator:
    index: str


@dataclass(frozen=True)
class EthCommittee:
    index: str
    validators: list[EthValidator]

    def to_dict(self):
        return {
            "index": self.index,
            "validators": [validator.__dict__ for validator in self.validators],
        }


@dataclass(frozen=True)
class EthConsensusBlock(Block):
    epoch: int
    committees: list[EthCommittee]

    def to_json(self):
        return json.dumps(
            {
                "block_number": self.block_number,
                "epoch": self.epoch,
                "committees": [committee.to_dict() for committee in self.committees],
            }
        )

    @classmethod
    def from_response(cls, slot: BlockNumber, data: dict[str, t.Any]):
        epoch = slot // 32
        committees = []
        for committee in data["data"]:
            validators = []
            for validator in committee["validators"]:
                validators.append(EthValidator(validator))
            committees.append(EthCommittee(committee["index"], validators))
        return EthConsensusBlock(slot, epoch, committees)

    def get_random_committee(self, rng: RNG) -> EthCommittee:
        return rng.random.choice(self.committees)

    def get_random_committee_index(self, rng: RNG) -> str:
        return self.get_random_committee(rng).index

    def get_random_validator_index(self, rng: RNG) -> str:
        return rng.random.choice(self.get_random_committee(rng).validators).index

    def get_random_validator_indexes(self, count: int, rng: RNG) -> list[str]:
        start_index = rng.random.randint(0, 128 - count)
        committee = self.get_random_committee(rng)
        return [validator.index for validator in committee.validators[start_index : start_index + count]]


class EthConsensusTestData(TestData[EthConsensusBlock]):
    def fetch_block_header(self, block_id: int | str) -> dict[str, t.Any]:
        block_response = self.client.get(f"/eth/v1/beacon/headers/{block_id}")
        if block_response.status_code == 404:
            raise BlockNotFoundError
        return block_response.json["data"]["header"]["message"]

    def fetch_block(self, block_id: int | str) -> EthConsensusBlock:
        if isinstance(block_id, str):
            if (block_id := block_id.lower()) not in (
                "head",
                "genesis",
                "finalized",
            ):
                raise ValueError("Invalid block identifier")
        slot = int(self.fetch_block_header(block_id)["slot"])

        committees_response = self.client.get(f"/eth/v1/beacon/states/{block_id}/committees", params={"slot": slot})
        return EthConsensusBlock.from_response(slot, committees_response.json)

    def fetch_latest_block(self) -> EthConsensusBlock:
        return self.fetch_block("head")

    def fetch_latest_block_number(self) -> BlockNumber:
        return int(self.fetch_block_header("head")["slot"])

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> BlockRange:
        end_block_number = self.fetch_latest_block_number()
        if parsed_options.use_latest_blocks:
            start_block_number = end_block_number - self.data.size.blocks_len + 1
        else:
            start_block_number = 1
        logger.info("Using blocks from %s to %s as test data", start_block_number, end_block_number)
        return BlockRange(start_block_number, end_block_number)

    def get_block_from_data(self, data: dict[str, t.Any] | str) -> EthConsensusBlock:
        def get_committee(committee: dict[str, t.Any]) -> EthCommittee:
            return EthCommittee(
                index=committee["index"],
                validators=[EthValidator(index=validator["index"]) for validator in committee["validators"]],
            )

        if isinstance(data, str):
            data_dict = json.loads(data)
        else:
            data_dict = data

        slot = data_dict["block_number"]
        epoch = slot // 32
        committees = [get_committee(committee) for committee in data_dict["committees"]]
        return EthConsensusBlock(slot, epoch, committees)

    def get_random_epoch(self, rng: RNG) -> Epoch:
        return self.get_random_block(rng).epoch

    @staticmethod
    def get_random_validator_status(rng: RNG) -> str:
        return rng.random.choice(EthValidatorStatuses)

import logging
import typing as t
from argparse import Namespace
from dataclasses import dataclass

import orjson as json
from tenacity import retry, stop_after_attempt

from chainbench.util.rng import RNG, get_rng

from ..util.http import JsonRpcError
from .blockchain import (
    Account,
    BlockHash,
    BlockNotFoundError,
    BlockNumber,
    BlockRange,
    InvalidBlockError,
    TestData,
    Tx,
    TxHash,
    append_if_not_none,
)
from .evm import EvmBlock

logger = logging.getLogger(__name__)

Slot = BlockNumber


@dataclass(frozen=True)
class SolanaBlock(EvmBlock):
    block_height: BlockNumber

    @classmethod
    def from_response(cls, slot: Slot, data: dict[str, t.Any]):
        block_height = data["blockHeight"]
        block_hash: BlockHash = data["blockhash"]
        txs: list[Tx] = data["transactions"]
        tx_hashes: list[TxHash] = []
        accounts: set[Account] = set()
        for index, tx in enumerate(txs):
            if index == 100:
                # limit it to 100 per block
                break
            append_if_not_none(txs, tx)
            append_if_not_none(tx_hashes, tx["transaction"]["signatures"][0])
            for account in tx["transaction"]["accountKeys"]:
                if account["pubkey"] != "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    append_if_not_none(accounts, account["pubkey"])
        return cls(slot, block_hash, txs, tx_hashes, list(accounts), block_height)


class SolanaTestData(TestData[SolanaBlock]):
    BLOCK_TIME = 0.4

    def get_block_from_data(self, data: dict[str, t.Any] | str) -> SolanaBlock:
        if isinstance(data, str):
            data_dict = json.loads(data)
        else:
            data_dict = data
        return SolanaBlock(**data_dict)

    def fetch_latest_block_number(self) -> Slot:
        slot = self.client.make_rpc_call("getLatestBlockhash")["context"]["slot"]
        return slot

    def fetch_block(self, slot: Slot) -> SolanaBlock:
        config_object = {
            "encoding": "json",
            "transactionDetails": "accounts",
            "rewards": False,
            "maxSupportedTransactionVersion": 0,
        }
        try:
            result = self.client.make_rpc_call("getBlock", [slot, config_object])
        except JsonRpcError as e:
            self._logger.error(f"Failed to fetch block {slot}: {e.code} {e.message}")
            print(f"Failed to fetch block {slot}: {e.code} {e.message}")

            if e.code in [-32004, -32007, -32014]:
                # block not found
                raise BlockNotFoundError()
            else:
                raise e

        block = SolanaBlock.from_response(slot, result)
        if len(block.txs) == 0:
            raise InvalidBlockError
        return block

    @retry(reraise=True, stop=stop_after_attempt(5))
    def fetch_latest_block(self) -> SolanaBlock:
        return self.fetch_block(self.fetch_latest_block_number())

    def _fetch_first_available_block(self) -> Slot:
        slot = self.client.make_rpc_call("getFirstAvailableBlock")
        return slot

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> BlockRange:
        end_block_number = self.fetch_latest_block_number()
        earliest_available_block_number = self._fetch_first_available_block()

        # factor in run_time and add 10% buffer to ensure blocks used in test data are
        # not removed from the ledger
        earliest_available_block_number += int((parsed_options.run_time / self.BLOCK_TIME) * 1.1)
        start_block_number = earliest_available_block_number

        if parsed_options.use_latest_blocks:
            start_block_number = end_block_number - self.data.size.blocks_len + 1

        if start_block_number < earliest_available_block_number:
            raise ValueError(
                f"Earliest available block (with buffer) is {earliest_available_block_number}, "
                f"but start block is {start_block_number}"
            )

        return BlockRange(start_block_number, end_block_number)

    def get_random_block_hash(self, rng: RNG | None = None) -> BlockHash:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).block_hash

    def get_random_block_height(self, rng: RNG | None = None) -> BlockNumber:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).block_height

    def get_random_tx_hash(self, rng: RNG | None = None) -> TxHash:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).get_random_tx_hash(rng)

    def get_random_tx(self, rng: RNG | None = None) -> Tx:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).get_random_tx(rng)

    def get_random_block_range(self, n: int, rng: RNG | None = None) -> BlockRange:
        if rng is None:
            rng = get_rng()
        if n >= (self.end_block_number - self.start_block_number):
            end = rng.random.randint(self.end_block_number - n, self.end_block_number)
            return BlockRange(end - n, end)
        else:
            start = rng.random.randint(self.start_block_number, self.end_block_number - n)
            return BlockRange(start, start + n)

    def get_random_account(self, rng: RNG | None = None) -> Account:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).get_random_account(rng)

    @staticmethod
    def get_random_token_address(rng: RNG | None = None) -> Account:
        if rng is None:
            rng = get_rng()
        token_addresses = [
            "z3dn17yLaGMKffVogeFHQ9zWVcXgqgf3PQnDsNs2g6M",  # Oxygen Protocol
            "2cZv8HrgcWSvC6n1uEiS48cEQGb1d3fiowP2rpa4wBL9",  # ACF Game
            "5fTwKZP2AK39LtFN9Ayppu6hdCVKfMGVm79F2EgHCtsi",  # WHEYO
            "NeonTjSjsuo3rexg9o6vHuMXw62f9V7zvmu8M8Zut44",  # Neon EVM
            "8BMzMi2XxZn9afRaMx5Z6fauk9foHXqV5cLTCYWRcVje",  # Staika
            "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",  # dogwifhat
            "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",  # Jupiter
            "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # Bonk
            "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",  # Pyth
        ]
        return rng.random.choice(token_addresses)

    @staticmethod
    def get_random_token_account(rng: RNG | None = None) -> Account:
        if rng is None:
            rng = get_rng()
        token_accounts = [
            "CF34PLYZfTMteS2mR3VzxsHjk6VXfCTnAcnwaEGJrknt",
            "97DxJzDxY71ofivxpNuNyKYcZy824zJWAXYemM5Md4Dt",
            "FE2BNorsuDMFDQ8XNkDfxp5x2H59qviowi39RVBzPf2S",
            "2CR6HNJrq8g6auzwpQiVP2TcbE2gAPZxGT16pTU6h13g",
            "4ZFd7tmfZzoyinBR1mWSr5FfmjdyvmbZ7DMMhUjrx7jW",
            "FTUTbTrWdxctBh4DrYTK8Scrtnj52KMSYbc1RS9ytF6J",
            "2eZAfcCyxPwxxqK9gVfzPcJH1jrnfa2xZggy1RFEiDHd",
            "6ttf7G7FR9GWqxiyCLFNaBTvwYzTLPdbbrNcRvShaqtS",
            "62KEKuC6yPmKy7M1PJjk8EWuouuF1srk4rxwPptsoySh",
            "EaDGsTov6CvsZZeo16cbrrtUE8J9gjkSPis5c6SiSHEH",
            "FcTsmtRX9wNFhiviJbW5YgG3PKXDNQtemQA5zNL2W1pW",
            "HmrKnggYYcNVwF8S7L1nno7LCKzobDBjX5UBuzFZukYj",
            "5nox3B41bSNtJV3s7gFPWVK8JtdaZ4QxCVxrhpGgnw4B",
            "GoBAZzgSLnoc5mXuUHgMLKsqYX7BFrdgwQYJL2cApgmX",
            "3GXyFi89uNvGPngFi65NYsWxxHTWDbJQtM1ntjGfn2gK",
            "4T6FHkAmoW21ia1GWDT5KBMd83kjwrPiXx4QYTkxz899",
            "FwrCxkDG1vahAHeGi1Wr5mBgLyayUvCy3d1tbnhsAQ99",
            "EYVDkQXrjNwwpxw3m2EojnFJgyTVuan77XxMs2hbBk34",
            "4BedR6CnQRtHq3aMVcHcFaU9sT1Wns2vEKah7ATFimY7",
            "3eApKHDU4GpXD2L1uZ3CQGMj2bAq6grhdZz9zsf9xacr",
            "8gesfhmNebstEuFovKzFgaeq5LPtjM2esrq6JA4eQadJ",
            "ANjPXGaMSho5dp5A78osdTAYhWrt8o2DVQEjPhd2pZrW",
            "EvcsKVtsH92KvvAfA6SbWGA4ShTTTsWZt48KTdCuCd3Y",
            "7znyJ3N4K26BmispS6z7TNWfar61KzFiqbx4pYmtG4dN",
            "3zQXNfbzwp9L3UbwMe3JsSjB6eT9Wcx8B5RQ2VS1G2fL",
            "7mfvcxhqSzqQ9iTHqDqugC3HVBcnvoFsdgWEjLyykx3E",
            "GJscPZ2xzayPa8QXW2Xi2WJPHaj2k1TQDShbhYJUHR94",
            "3shgyeu9cy8xkkRwDENKnsYXxsCUkc5suq3aYXi912XW",
            "3FGoU3eRepLeK5ZD1jA4GhSWw7GUYhsJwPBB5Qfihrmt",
            "3voYsgqCZEWvyG8xSkNhgqYb9ciKNjzXX91JwesqdasT",
            "G58QLCn2H2TvtoPT5uwT8tjpYAUa1CzWsbKJXUPqMaJ4",
            "J5jtM83Eoyn1TQdxu1hRC96dLy4ZgenN9vf6Fk5jLe9V",
            "GvZ4emMJfgW9U2nfw145FraS2BMJyGsmoji8eWi11d6j",
            "DugPkEmWHgTSXNMGAD9r3SbL7MgDrnuHuSeH695tN8FQ",
            "39uZe8NUJJVnNmQ6nA6VxQFwQ3GqypvtVrnhSLbByRBr",
            "8zBEBGcPZBVqu6fRmxsiXCEG4ehvh3TEiy8gq6q6E6YL",
            "4bEcyAvz5zSzFwAnEAHGSsUG1EASMnbJSDPSipPKStti",
            "DTbktzGachmQVW1sH7sNxCYrs3YpcEtyDuBcHAWr6y3t",
            "HQvP9mRNpZBXi3CMsp2vP2H8qaGAFeQobArX455Ugoh9",
            "4iSr7wAsfe9ohXSS2Z6v2icV94X81hPtPLLvt6ss84yb",
            "3d1Vr3n7cdzhk3vrSn2eXm8H3gqSircLVqwqcEKc4AX2",
            "4zHS6gTzBRXpJojhJgHQRCVYhMAdDBHW2QSU7SNMtXh9",
            "JguSE1vBoUUSN7MxZBHKJHjXxECW7d12xLPLzVV7SYi",
            "zGWrqUkuhmtHA8G7JJ3mxbbAxxRYpC2GXWnKyYMFDM2",
            "4ehpyuufJtzt49CtJYaN3HLDYYMotvR34WKkFBNe4fDv",
            "HsrDHXyWT6gNPnHPSMgoHpQxLSqMcsyJCXLvp4oxhoV7",
            "B4kZTkeZCTnHf3J6pWC9deHUx4BWU8cZPewY6PtWYS3s",
            "HjVvBA8HX3ZxA9wAziApGXTQsZnLTtDxQa9ymSCkke64",
            "8M23uCAp1Wc3jTKhq7nzTxqKK54XVdDwSLspv1x4Yigs",
            "DW8awKneKxcep9iouLeNwWRAzC6rz9sLKAgENpXL6BBd",
            "HU5CJ61HKmWfBzK6jrD2q6o17iwrkf3T9xqrdBgPBR5F",
            "2yobwT8wsq6y4fbEkdnZk5Mj42hiAZW6tyiLU4KjhPVc",
            "9vujwMDWRHfXSHs1oTEUXcUUwWmev4gf2mzJ2FzNbmkq",
            "2wkdLjUEmaQ88Ut1hi5vRFoFgSpovz8x9xj8nhURTKJB",
            "Cdigh3iZD8DvHTnNyC4Sm7uiNhiFmY2EcpfCviLG2AEC",
            "7ZHAcG8T12tWeSgvvTNDE3hskFfXRaVe3PRMjvEAzCC4",
            "5m1gS9Sphbvt4zDCu6gqFqVcekCX8eAtfwJjPDMUVvxJ",
            "9HHMyRMeYSyeR45LSnHHvpofq8cnX2dShUg5zmHsDpiA",
            "4WMDNjMpKLEbC4oqAeTchN5WjwjJrnZdTzmpTqdeJoc8",
            "r1RNBu4Grexhe9AsK1cakgyzh93uxmXzeKk7jApVhKf",
            "CfE7AzLsSsEBSsQgWAvXes9qfQmE7WYJTdApMefu8ZaM",
            "HSizfxkFyeUssoVvzgjkgArQ4RFyKZWMmHU554Ya9V6R",
            "9okWmESkYFw3Jmk3KxRijp2TMM21YHAGaUFRZNUoDFjP",
            "FRojFj9xyuFtePNn4xuqPzZU8CLyLpAaYPwf7aG8gotJ",
            "A5zrmTFMPpTWhSxay8gDr3rLr4WguCPYp8um5ywRFeCT",
            "8VWPNtQvjSGrot14cgBSgNDKJhLvFaodcpY9dFGZJx1z",
            "3PqVf4rm7Yx1GqdND9Q6mMormXfFZRvTJdBFwBEGdobB",
            "C3EJkyHWfAn9mZBi6SneEp57VvpYNxVnqE9AtwmvAuo",
            "9x2FRfDMAiDBSZPR5HJje6bpAH8XHkeqedBopbwu9g1H",
            "gi9vP3V2p5mDYURGNo7CPcEfR1tMp3sxjbQ1AHvpyxZ",
            "BbLCUYHyYcRJCfzgoow96MSMb3EKdHWL4ALq3YNJpA2z",
            "HfAK56UE6pLwBM1kQxn1vAk5W6sRBrSE8KrndCooR5Kx",
            "G6g2193UQA3N8byF9D7cDn5tYhAt6gbNB9zLNHZYJJaH",
            "3MXL9RNyHJcg3wYUBsbDLQyNTyJJRftZMzg7bxPsdFGf",
            "3bFoTw6XoeuYd1qMCQCQTf7EJoQHXjgJUB8W9FoSESY1",
            "BxQSVGUcfWt2k5AZ58rKxwxdCau2NXa9yt9osmDWU9hJ",
            "GSHsTFMNMtAyFP6PxDKvTHDDBzzZYUFQnqFumtcLFicc",
            "Fm5iBQMZxuH5XMNMd7RcfYxQuxhGNXsLZ5SZ5rLXnCGF",
            "6Y7xRKGwL1ok12NnkwNhAtumqb7ugZ9xvCYrnMB8Xviv",
            "H4BdrSaFofoeQRUH4g5fY9tgRc1yqCdEryETKnW26tbm",
            "CTh1akv2g7hRsBUFdjLrNW6TzAe34AukJBNsYw5sUH5s",
            "6fbPJiBdXAoN4qkXuxMwUNZUF77WxfeDPCznWCxVPdL2",
            "C4hXRxKmfucqNDndwYASSDm7EbPcoXG3LPFULdXP5MUh",
            "8kfrPrNzFv3ouvQBP4JwmA9upRu4uDAXf8WP7gmsRevA",
            "8PvETn7pxGE7ZwLUxQbob3zXcx8SFYEaKujWXkVdyzy8",
            "86nsBYZV6UyuiRqK5PyMKpbJAMkay7aLyfBieYjFw383",
            "7LBGStihbxoBAWtqDiVzTSg8ci6y74Ws2bbd2xiyXk35",
            "DGKpmnNkmKzgMsrJQsP9dYzxRChcf5PbhDA8Z24Mm9L9",
            "3Xjac1TpCgtW8U5RBenzmWwUfsNXhNAn7jdvvgURDped",
            "GLVvAEsrWc5vhknQdkVyDkyzgQ2kFzh4NhfqADYxzLZb",
            "9YzDwNLK5C7ZEKhYiNt27gbNejpdEoeTfKyTFwDsjfgy",
            "7Xi29v2bqBx4DNbVq1LA8WJPuyLiRPqCxxBBZBnNsumu",
            "BKqEQy6E4Pa2yAEssbQS1PfbjQCfKSmrjqNCtemY8dKk",
            "TsG1nsBvMxKULXtiAgH3iUatrFzihw9MgHyz6VGHSSJ",
            "HthTrkvsRA1sAuWRJmP4UAB37VT2RTgT7QFWvWKMRey",
            "5SR9UtKUJpXRFd3W1bnNjS44vJuoFQyAznoESzGA7M1r",
            "Eqz4J57GkmPq2P2U8yWGQspUB8FWBLnidoPhMcvWS1Jx",
            "A6JCe9BDEby7fsevUbzTqU9jFBbkHwSuDmJGhoPLy44L",
            "Grh57JBjPDYeTwSqNsQ8i3ks2HJsq5HxCFHpqhNcWiDi",
            "CDeni3XaGkCrbN8Wm2PwmFHnk3ce9cEFbitRC1NNxxrE",
            "7XX64f8UKE1nxNCSwncCUj3c2FJYdXHmDV5xd5DRdFky",
            "EHDnHqX6PtnSdPfsnnr1oWtmQbenDwqZAKUo5QAq9Ro3",
            "1LLLyMZvAdimbcsC4Xp7GVWiJScztEpfXVR9upyxq5G",
            "DsxpGaCZ13aUfDDz2CSjuzCA8XJJYLuGsV65KXdyLWdW",
            "Fm7yBTcuUDBdzj2PbP6tr8uiFAJwS53kNQbwEERHP65A",
            "EdhM4qGK29P2X1GsRYZtF8E5v9rkd52NRXEh1d8BzUc8",
            "4kT3EXc5dDVndUU9mV6EH3Jh3CSEvpcCZjuMkwqrtxUy",
            "GqzXwoPv8TJtxqDDB1G3Q35MQpor6433fdB18vdNYfqC",
            "AaJyLPfJoJFcUHHH7VDWsqyVPb7aMAwcRHB2Z7YXt2La",
            "6sJ9tDgWmQxkEZSk8xihYiJUpmFL3fdgLQ6DayCSDR2U",
            "7VKFsPJooGLrWvMqyjvfTucUQRKzop6iErPGw4S2r69K",
            "DNnGKYfnrQirEr2Z1145WLLtRCwtaZh8PpzijrWUDKMr",
            "3MWHzLgLQ98n4htEJXKJWNUNUfbeexWEDnksRFxDsLeS",
            "6fafNTqhRyQ4Q3cwD9VVhXZAVCtL1YYW2kSKTD3ytBse",
            "AUmMMDCvmghtsrn5T6EzcJBiaSApv5P4d2XVQdZAg1vp",
            "BADVD1RWzAXDd62Fj6RPTnmFwXxviRjxpvSaidarHDc9",
            "2Dyj8L9kv4wSK4sXyfcduoYoPUouSQWsuv9THm11cvEh",
            "GygCQjU9eTr3WivrstviJhJqbDL4tnoAjGXCGo1XzEub",
            "CBzCGSmuNKKrGjMQLQ1ihkbVUJRATavcsd6rdiZ2CFv7",
            "pC2qrgQNnKZ87JxBrULrZiLhEQim8SpchAxAKnqDnya",
            "26ddLrqXDext6caX1gRxARePN4kzajyGiAUz9JmzmTGQ",
            "6G4XDSge4txj5tBkA5gZqefXXE3BRxqA37Yb1pmrHv6N",
            "7bEL9XkPGNg7a3oSiUERKsZtFoJMqKh6VhGDCmMCPqdg",
            "K6U4dQ8jANMEqQQycXYiDcf3172NGefpQBzdDbavQbA",
            "GDijXRGfd1jhk5GkRPp1TDnEH2FfHURSRZeB5um3pUWk",
            "DWVtxR7oo3uTiuM3o1cCxTJ5wM8Wnjvu1apwMkQhdedY",
            "B3NG3yTDwf3sL1oCUvf39HtdzWbtYoinNWqKDoRJTeuH",
            "CeLRs4kchQbWEcqZf7ctGrYhXwbU89fVxRs4Q34XeiHq",
            "GQrdtzmAsXpb5pPsENC68jXF6YwmME235ZJpRoKh5F5R",
            "ASehmX2sjG1Qz7MQyLJu8wBoV2Xx8cCV3uU8VbBDGQJQ",
            "649KG5AEPic6MDVdbXjLPWj3vy6Lc466qGjV9d5Y3VyZ",
            "FGHwSJMx8yvMMmfiZSd5jmL7KbbbubVpNrhYX7NXPCdu",
            "E6FLdjDBtHvzhMGihcbec34KfcAqSYW67kfJV8RAKH1f",
            "mGmik7Qf2YdrSZjTsS3ciZn4xyqiVHYUP7cfjQDT5he",
            "6QxycVhn6Zak2ky4HAEEanz85ockBaEfHxgtqPP7Mo1a",
            "FErFdzAFoA26ASDz9zh4Jan3hV2wRb32Mc1MFMXr7n51",
            "Ek7bER9cRJZVHE7Zzmig31PbqT9KkkjAKAgqnyof6JAk",
            "EbX6N2wuAAiF6WMnQPG15kq18nx2yApg9ikawxDHBi7j",
            "2V9CYburvmC2X2w96HFreUd9iEcW7BdWTFTJCt46tuai",
            "AbJpTjriAPp4Vuv5xjoWQHjh68NVSw36Wmky2hQVJJzP",
            "F8FqZuUKfoy58aHLW6bfeEhfW9sTtJyqFTqnxVmGZ6dU",
            "5hpfC9VBxVcoW9opCnM2PqR6YWRLBzrBpabJTZnwwNiw",
            "4XHP9YQeeXPXHAjNXuKio1na1ypcxFSqFYBHtptQticd",
            "JDPR4RP95CdtwLcjqe3E4cVthzCmkASfs4yamN9MZyPR",
            "CDV3tvd7XwNez9crbEmJpPjdNXceM1Ro5iHqTiaUKt2w",
            "6xAckK4UWmaX4CKu27oPzHLxMKzaDMj73WA9xKpqSFQ1",
            "9Vfbb8i2Z6WjDJwZEfmhwTk4paCpTYcyJgNFdns2GV2s",
            "2UfAKNkmBWjad3qKnFCRfzbHwwhgU5eBs2DDXSJBMVSb",
            "9uEDvRyhqygr6SrmvddRDaFbdsazQzuPQCsDewpwfbqh",
            "7FdQsXmCW3N5JQbknj3F9Yqq73er9VZJjGhEEMS8Ct2A",
            "AoEkWJKHXzrPsgsoawYTLG3aKb9L8oLmVqM9EXFtiPN7",
            "7a7iBY13WPKfSpkA1WMpoJB59NE2zr255THWg7GyVb1q",
            "7csLUpezHQH7f5uha3s93ruKutcniNQmxjmapRsrfxaR",
            "6jFRDDFQDCasLcWVMtixuu1eQCDnMhCttXktVeL7cEYM",
            "ATbwzBwGNM8QjLwPGk8PJz8FgCmfWfRud1zB8Zs6tLEb",
            "HJbmekvxyMuVjTV2gZKgdBYx94Bumugtt1GrWKBkTv5X",
            "AsBeRcytoLArFXwzovGH2gamp9by5B9V1TemMT5LDyQH",
            "3pY1zLGNXnQedWwCQeaaHK9dQCsfqMCRPzVD3DnZwSsd",
            "29zZdccuHktabvWwJaEokASw6pPBDVpqBDZxTicMhM1R",
            "GKD5CK5SqpB66taGqTwGy1FCTyzKrxhyrY7V68aKpoVC",
            "Eq9dm4pHewdSVaKdpVJogjLW6upd9hNkiboX2eSncmFV",
            "23KfDBTdpaBqfn8aUeoEDgfGJ5368gpnyYGfNkKcECqM",
            "5ULtZcyfuWvKuwB555WN4W1vsVW4F3yHU9UW1Gd7kAWy",
            "ADBN766ykF4HdkNa7Az8BVrpaQdvSpaMMULufBAs8U1B",
            "61YcP8msC5F3ZTLy99VWM2oom6y47UzNmSQQdXMmdCG1",
            "984XkyV6X29LUYSi476KC5cTFNMyegrx81EfHj6qWSeV",
            "DXu8wVJigvqBLNf18QYQbHn7hcvVWnCpCMoYAPuQGEyr",
            "7p1D1WBPr3sK9TYwrRwVcjYwacXhMH3WdJqqyowbvD1f",
            "52AXihP4T7dgtfxFMjjLBFVGucNvHmxMW5GkvM1vQyFU",
            "HmBHnMwfmsuEFZ4pFpYAXeAkcdnbWzCGEwZ2SXjY8W3N",
            "3XSoALqyVbG1ZMgmTwNcuUf294LzjUj7Mvy7MgA7YNVk",
            "Gnyw7rZykLq9FjLMzsu6nAryMJijy5FjCEbxxdkymRwk",
            "4QJg58aV3UUi2CJ99kiqCMizY81w513qvaQoNgPERHBn",
            "FQ2yHp7D3SBYQoe2crFATJdhsazJKJ9Yvq4xFbTzCMYx",
            "GSmbMHXC6czx77qXWT3UH1jg2jW6SWdD6D6mFFx3rYmY",
            "JDFgtub1sDznJgJRYbHZu1tGQsnhrz17gv8Arq8Zc1SL",
            "6BQsUwpVwmPyjGfpE3BAUsNmmbcVy9ygyDYXfpFZ785Z",
            "ACthtigKSdBXfCKLUfZNjQzLMmKHzjbSafqpa1NJ3M7J",
            "9omg1BYxdA3hhM1rmx3tpMnTf9aqzBRUE9bV6i77b88M",
            "HwyjTsHYceVsnhH3Suda9VSqtXftuN9wwjt4aUEx6C3T",
        ]

        return rng.random.choice(token_accounts)

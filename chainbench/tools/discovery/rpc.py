import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from tenacity import retry, retry_if_exception_type, wait_exponential

from chainbench.util.http import HttpClient, HttpErrorLevel

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class TooManyRequestsError(Exception):
    pass


@dataclass
class RpcMethod:
    name: str
    supported_clients: list[str]


@dataclass
class RpcClient:
    name: str
    version: str
    endpoints: list[str]

    def get_cli_argument_names(self) -> Iterator[str]:
        if len(self.endpoints) > 0:
            for endpoint in self.endpoints:
                yield f"{self.name}{endpoint}"
        else:
            yield self.name

    def get_name_and_version(self) -> Iterator[str]:
        for name in self.get_cli_argument_names():
            yield f"{name}: {self.version}"


@dataclass
class DiscoveryResult:
    method: str
    supported: bool | None = None
    error_message: str | None = None

    def to_string(self) -> str:
        if self.supported is True:
            return f"{self.method}, ✔"
        elif self.supported is False:
            return f"{self.method}, ✖"
        else:
            return f"{self.method}, {self.error_message}"


class RpcDiscovery:
    METHODS_FILE = Path(os.path.join(__location__, "methods.json"))
    CLIENTS_FILE = Path(os.path.join(__location__, "clients.json"))

    def __init__(self, endpoint: str, clients: list[str]):
        self.endpoint = endpoint
        self.clients = clients

        self.methods = self.get_methods_list(clients)
        self.http = HttpClient(self.endpoint, timeout=5, error_level=HttpErrorLevel.ServerError)

    @staticmethod
    def _parse_methods() -> list[RpcMethod]:
        methods = []
        methods_json = json.loads(RpcDiscovery.METHODS_FILE.read_text())
        for method in methods_json.keys():
            methods.append(RpcMethod(name=method, supported_clients=methods_json[method]["clients"]))
        return methods

    @staticmethod
    def _parse_clients() -> list[RpcClient]:
        clients: list[RpcClient] = []
        clients_json = json.loads(RpcDiscovery.CLIENTS_FILE.read_text())
        for client in clients_json.keys():
            if "endpoints" in clients_json[client]:
                endpoints = clients_json[client]["endpoints"]
            else:
                endpoints = []
            clients.append(RpcClient(name=client, version=clients_json[client]["version"], endpoints=endpoints))
        return clients

    @classmethod
    def get_methods_list(cls, clients: list[str]) -> list[str]:
        methods = []
        for method in cls._parse_methods():
            for client in clients:
                if client in method.supported_clients:
                    if method.name not in methods:
                        methods.append(method.name)
        return methods

    @classmethod
    def get_client_names(cls) -> list[str]:
        return [client.name for client in cls._parse_clients()]

    @classmethod
    def get_clients(cls) -> list[RpcClient]:
        return cls._parse_clients()

    @retry(retry=retry_if_exception_type(TooManyRequestsError), wait=wait_exponential(multiplier=1, min=2, max=10))
    def discover_method(self, method: str) -> DiscoveryResult:
        def check_response() -> DiscoveryResult:
            keywords = ["not supported", "unsupported"]

            if response.status_code == 429:
                raise TooManyRequestsError

            # Some providers return 400 for missing params, so we want to ignore that error
            if response.status_code not in [200, 400]:
                return DiscoveryResult(method, None, f"HTTP error {response.status_code}")
            try:
                if "error" in response.json:
                    error_code = response.json["error"]["code"]
                    # Some providers return -32600 or -32604 for unsupported methods
                    if error_code in [-32600, -32604]:
                        for keyword in keywords:
                            if keyword in response.json["error"]["message"].lower():
                                return DiscoveryResult(method, False)
                    if error_code == -32601:
                        return DiscoveryResult(method, False)
                    if error_code == -32602:
                        return DiscoveryResult(method, True)
                    return DiscoveryResult(
                        method,
                        None,
                        f"Unable to determine. Unknown error {response.json['error']['code']}: "
                        f"{response.json['error']['message']}",
                    )
                return DiscoveryResult(method, True)
            except ValueError:
                return DiscoveryResult(method, None, f"Value error {response.json}")

        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": method,
            "params": [],
        }
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
            }
            response = self.http.post(data=data, headers=headers)
            result = check_response()
            return result
        except TimeoutError as e:
            return DiscoveryResult(method, None, f"HTTP Timeout Exception: {e}")

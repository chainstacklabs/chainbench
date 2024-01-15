import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import httpx

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


@dataclass
class RPCMethod:
    name: str
    supported_clients: list[str]


@dataclass
class RPCClient:
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


class RPCDiscovery:
    METHODS_FILE = Path(os.path.join(__location__, "methods.json"))
    CLIENTS_FILE = Path(os.path.join(__location__, "clients.json"))

    def __init__(self, endpoint: str, clients: list[str]):
        self.endpoint = endpoint
        self.clients = clients

        self.methods = self.get_methods_list(clients)
        self.http = httpx.Client()

    @staticmethod
    def _parse_methods() -> list[RPCMethod]:
        methods = []
        methods_json = json.loads(RPCDiscovery.METHODS_FILE.read_text())
        for method in methods_json.keys():
            methods.append(RPCMethod(name=method, supported_clients=methods_json[method]["clients"]))
        return methods

    @staticmethod
    def _parse_clients() -> list[RPCClient]:
        clients = []
        clients_json = json.loads(RPCDiscovery.CLIENTS_FILE.read_text())
        for client in clients_json.keys():
            if "endpoints" in clients_json[client]:
                endpoints = clients_json[client]["endpoints"]
            else:
                endpoints = []
            clients.append(RPCClient(name=client, version=clients_json[client]["version"], endpoints=endpoints))
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
    def get_clients(cls) -> list[RPCClient]:
        return cls._parse_clients()

    @classmethod
    def check_response(cls, method: str, response: httpx.Response) -> DiscoveryResult:
        keywords = ["not supported", "unsupported"]

        if response.status_code not in [200, 400]:
            return DiscoveryResult(method, None, f"HTTP error {response.status_code}")
        try:
            response_json = response.json()
            if "error" in response_json:
                error_code = response_json["error"]["code"]
                if error_code in [-32600, -32604]:
                    for keyword in keywords:
                        if keyword in response_json["error"]["message"].lower():
                            return DiscoveryResult(method, False)
                if error_code == -32601:
                    return DiscoveryResult(method, False)
                if error_code == -32602:
                    return DiscoveryResult(method, True)
                return DiscoveryResult(
                    method,
                    None,
                    f"Unable to determine. Unknown error {response_json['error']['code']}: "
                    f"{response_json['error']['message']}",
                )
            return DiscoveryResult(method, True)
        except ValueError:
            return DiscoveryResult(method, None, f"Value error {response.json()}")

    def discover_method(self, method: str) -> DiscoveryResult:
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
            response = self.http.post(self.endpoint, json=data, headers=headers)
            return self.check_response(method, response)

        except httpx.TimeoutException as e:
            return DiscoveryResult(method, None, f"HTTP Timeout Exception: {e}")

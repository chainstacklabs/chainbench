import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import httpx

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class JSONRPCError(Exception):
    pass


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


class RPCDiscovery:
    METHODS_FILE = Path(os.path.join(__location__, "methods.json"))
    CLIENTS_FILE = Path(os.path.join(__location__, "clients.json"))

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
    def _get_methods_list(cls, clients: list[str]) -> list[str]:
        methods = []
        for method in cls._parse_methods():
            for client in clients:
                if client in method.supported_clients:
                    methods.append(method.name)
        return methods

    @classmethod
    def get_client_names(cls) -> list[str]:
        return [client.name for client in cls._parse_clients()]

    @classmethod
    def get_clients(cls) -> list[RPCClient]:
        return cls._parse_clients()

    @classmethod
    def discover_methods(cls, endpoint: str, clients: list[str]) -> list[DiscoveryResult]:
        result: list[DiscoveryResult] = []
        http = httpx.Client(base_url=endpoint)

        method_list = cls._get_methods_list(clients)

        for method in method_list:
            data = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": method,
                "params": [],
            }
            response = http.post(endpoint, json=data)
            if response.status_code != 200:
                print(f"HTTP Error {response.status_code} with method {method}")
            else:
                response_json = response.json()
                if "error" in response_json:
                    if response_json["error"]["code"] == -32602:
                        result.append(DiscoveryResult(method, True))
                    elif response_json["error"]["code"] == -32601:
                        result.append(DiscoveryResult(method, False))
                    else:
                        result.append(
                            DiscoveryResult(
                                method,
                                None,
                                f"Unable to determine. Unknown error {response_json['error']['code']}: "
                                f"{response_json['error']['message']}",
                            )
                        )
                else:
                    result.append(DiscoveryResult(method, True))
        return result

import json

import httpx


class JSONRPCError(Exception):
    pass


class RPCDiscovery:
    @staticmethod
    def _get_methods_list(clients: list[str]) -> list[str]:
        methods = []
        with open("chainbench/tools/discovery/methods.json", "r") as f:
            methods_json = json.loads(f.read())
            for method in methods_json.keys():
                for client in clients:
                    if client in methods_json[method]["clients"]:
                        methods.append(method)
        return methods

    @staticmethod
    def get_clients_and_versions() -> list[tuple[str, str]]:
        clients = []
        with open("chainbench/tools/discovery/clients.json", "r") as f:
            clients_json = json.loads(f.read())
            for client in clients_json.keys():
                if "endpoints" not in clients_json[client]:
                    clients.append((client, clients_json[client]["version"]))
                else:
                    for endpoint in clients_json[client]["endpoints"]:
                        clients.append((f"{client}{endpoint}", clients_json[client]["version"]))
        return clients

    @classmethod
    def discover_methods(cls, endpoint: str, clients: list[str]) -> list[tuple[str, str | bool]]:
        result: list[tuple[str, str | bool]] = []
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
                        result.append((method, True))
                    elif response_json["error"]["code"] == -32601:
                        result.append((method, False))
                    else:
                        result.append(
                            (
                                method,
                                f"Unable to determine. Unknown error {response_json['error']['code']}: "
                                f"{response_json['error']['message']}",
                            )
                        )
                else:
                    result.append((method, True))
        return result

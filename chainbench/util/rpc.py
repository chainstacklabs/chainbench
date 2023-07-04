def generate_request(method, params: list | None = None, version: str = "2.0"):
    """Generate a JSON-RPC request."""
    if params is None:
        params = []

    return {
        "jsonrpc": version,
        "method": method,
        "params": params,
        "id": 1,
    }

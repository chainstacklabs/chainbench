import json
import logging
import typing as t
from enum import IntEnum
from functools import cached_property
from json import JSONDecodeError
from secrets import token_hex

from geventhttpclient import URL, HTTPClient
from geventhttpclient.response import HTTPSocketPoolResponse

logger = logging.getLogger(__name__)


class HttpErrorLevel(IntEnum):
    ClientError = 400
    ServerError = 500


class HttpStatusError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"HTTP Status Error: {code} - {message}")


class JsonRpcError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"JSON RPC Error: {code} - {message}")


class Response(HTTPSocketPoolResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def content(self) -> str:
        return self.read().decode("utf-8")

    @cached_property
    def json(self) -> dict[str, t.Any]:
        # check if response is json
        try:
            data: dict[str, t.Any] = json.loads(self.content)
        except JSONDecodeError:
            logger.error("Response is not json: %s", self.content)
            raise
        else:
            logger.debug(f"Response: {self.content}")
            return data

    def check_http_error(self, request_uri: str = "", error_level: HttpErrorLevel = HttpErrorLevel.ClientError) -> None:
        logger.debug(f"Request: {self.method} {request_uri}")

        if self.status_code < error_level:
            return
        """Check the response for errors."""
        if self.status_code >= error_level:
            logger.info(f"Request failed with {self.status_code} code")
            logger.debug(
                f"Request to {request_uri} failed with HTTP Error {self.status_code} {self.status_message} code: "
                f"{self.content}"
            )
            raise HttpStatusError(self.status_code, self.status_message)


class HttpClient:
    def __init__(
        self,
        host: str,
        rpc_version: str = "2.0",
        timeout: int = 360,
        error_level: HttpErrorLevel = HttpErrorLevel.ClientError,
    ):
        self._rpc_version = rpc_version
        self._host = URL(host)
        self._client = HTTPClient.from_url(self._host, connection_timeout=120, network_timeout=timeout)
        self.error_level = error_level

    @property
    def host(self) -> str:
        return str(self._host)

    def close(self) -> None:
        self._client.close()

    def _request_uri(self, path: str = "", params: dict[str, t.Any] | None = None) -> str:
        if len(path) > 0 and path[0] != "/":
            path = "/" + path
        return URL(self.host + path, params=params).request_uri

    def get(
        self,
        path: str = "",
        params: dict[str, t.Any] | None = None,
        headers: dict[str, t.Any] | None = None,
        error_level: HttpErrorLevel | None = None,
    ) -> Response:
        if headers is None:
            headers = {}
        if "Accept" not in headers:
            headers.update({"Accept": "application/json"})
        response = self._client.get(
            self._request_uri(path, params),
            headers=headers,
        )
        response.__class__ = Response
        if error_level is None:
            error_level = self.error_level
        response.check_http_error(self._request_uri(path, params), error_level)
        return response

    def post(
        self,
        path: str = "",
        data: dict[str, t.Any] | bytes | None = None,
        params: dict[str, t.Any] | None = None,
        headers: dict[str, t.Any] | None = None,
        error_level: HttpErrorLevel | None = None,
    ) -> Response:
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers.update({"Content-Type": "application/json"})
        if "Accept" not in headers:
            headers.update({"Accept": "application/json"})
        if isinstance(data, dict):
            body = json.dumps(data).encode("utf-8")
        elif isinstance(data, bytes):
            body = data
        else:
            body = b""
        response = self._client.post(
            self._request_uri(path, params),
            body=body,
            headers=headers,
        )
        response.__class__ = Response
        if error_level is None:
            error_level = self.error_level
        response.check_http_error(self._request_uri(path, params), error_level)
        return response

    def _make_body(self, method: str, params: list[t.Any]) -> dict[str, t.Any]:
        return {
            "jsonrpc": self._rpc_version,
            "method": method,
            "params": params,
            "id": token_hex(8),
        }

    def make_rpc_call(self, method: str, params: list[t.Any] | None = None) -> t.Any:
        if params is None:
            params = []

        response = self.post(data=self._make_body(method, params))

        logger.debug(f"Making call to {self._host} with method {method} and params {params}")
        logger.debug(f"Response: {response.json}")

        # check if response is error
        if "error" in response.json:
            logger.error("Response is error: %s", response.json["error"]["message"])
            raise JsonRpcError(code=response.json["error"]["code"], message=response.json["error"]["message"])

        # check if response is valid
        if "result" not in response.json:
            logger.error("Response is not valid: %s", response.json)
            raise ValueError(response.json)

        return response.json["result"]

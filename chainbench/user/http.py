import logging
import typing as t

from locust import FastHttpUser, TaskSet
from locust.contrib.fasthttp import ResponseContextManager

from chainbench.test_data import TestData
from chainbench.util.jsonrpc import expand_to_list


class HttpUser(FastHttpUser):
    """Extension of FastHttpUser for Chainbench."""

    abstract = True
    test_data: TestData = TestData()
    logger = logging.getLogger(__name__)

    connection_timeout = 120
    network_timeout = 360

    def on_start(self) -> None:
        self.test_data.wait()

    def on_stop(self) -> None:
        self.test_data.close()

    @staticmethod
    def task_to_method(task_name: str) -> str:
        raise NotImplementedError

    @staticmethod
    def method_to_function_name(method: str) -> str:
        raise NotImplementedError

    @classmethod
    def method_to_task_function(cls, method: str) -> t.Callable:
        method_name = cls.method_to_function_name(method)
        if not method_name.endswith("task"):
            method_name = method_name + "_task"
        return getattr(cls, method_name)

    @classmethod
    def expand_tasks(cls, load_profile: dict[t.Callable, int]) -> list[t.Callable | TaskSet]:
        tasks = expand_to_list(
            {cls.method_to_task_function(method.__name__): weight for method, weight in load_profile.items()}
        )

        return tasks

    def check_fatal(self, response: ResponseContextManager) -> None:
        if response.status_code == 401:
            self.logger.critical(f"Unauthorized request to {response.url}")
        elif response.status_code == 404:
            self.logger.critical(f"Not found: {response.url}")
        elif 500 <= response.status_code <= 599:
            self.logger.critical(f"Got internal server error when requesting {response.url}")
        elif 300 <= response.status_code <= 399:
            self.logger.critical(f"Redirect error: {response.url}")

    def check_http_error(self, response: ResponseContextManager) -> None:
        """Check the response for errors."""
        if response.status_code != 200:
            self.logger.error(f"Request failed with {response.status_code} code")
            self.logger.debug(
                f"Request to {response.url} failed with HTTP Error {response.status_code} code: {response.text}"
            )
            self.check_fatal(response)
            response.failure(f"Request failed with {response.status_code} code")
            response.raise_for_status()

    def post(
        self, name: str, data: t.Optional[dict] = None, params: t.Optional[dict] = None, path: str = ""
    ) -> ResponseContextManager:
        with self.client.request("POST", path, json=data, params=params, name=name, catch_response=True) as response:
            self.check_http_error(response)
            return response

    def get(self, name: str, params: t.Optional[dict] = None, path: str = "") -> ResponseContextManager:
        with self.client.request("GET", path, params=params, name=name, catch_response=True) as response:
            self.check_http_error(response)
            return response

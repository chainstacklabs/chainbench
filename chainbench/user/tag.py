import typing as t

from locust.user.task import TaskSet, TaskT


def tag(*tags: str) -> t.Callable[[TaskT], TaskT]:
    def decorator_func(decorated):
        if "locust_tag_set" not in decorated.__dict__:
            decorated.locust_tag_set = set(tags)
        return decorated

    if len(tags) == 0 or callable(tags[0]):
        raise ValueError("No tag name was supplied")

    return decorator_func


def clear_tags(tasks: list[t.Callable | TaskSet]):
    for task in tasks:
        if hasattr(task, "locust_tag_set"):
            task.__delattr__("locust_tag_set")

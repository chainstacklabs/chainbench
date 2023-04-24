import typing as t
from dataclasses import InitVar, dataclass, field
from enum import IntEnum
from pathlib import Path

import httpx

DEFAULT_NTFY_SERVER = "https://ntfy.sh"


class Priority(IntEnum):
    """Priority levels for notifications."""

    MIN = 0
    LOW = 1
    DEFAULT = 2
    HIGH = 3
    MAX = 4


class _NotificationData(t.TypedDict):
    """Notification request data."""

    content: bytes
    headers: dict[str, str]


@dataclass
class Notification:
    """A notification to be sent to a notification service."""

    message: str = ""
    title: str = ""
    priority: int = field(default=2)
    tags: list[str] = field(default_factory=list)

    email: str | None = field(default=None, repr=False, compare=False)
    file: InitVar[str | Path | None] = field(default=None, repr=False, compare=False)
    _file: Path | None = field(init=False, default=None, repr=False, compare=False)

    def __post_init__(self, file: str | Path | None = None) -> None:
        self.title = self.title.strip()
        self.message = self.message.strip()

        if file:
            self._file = Path(file)

    def _headers(self) -> dict[str, str]:
        """Return the headers to send to the notification service."""
        headers = {"X-Priority": str(self.priority)}

        if self.title:
            headers["X-Title"] = self.title

        if self.tags:
            headers["X-Tags"] = ",".join(self.tags)

        if self._file and self._file.exists():
            headers["X-Filename"] = self._file.name

        if self.email:
            headers["X-Email"] = self.email

        return headers

    def _content(self) -> bytes:
        """Return the binary content to send to the notification service."""
        if self._file and self._file.exists():
            return self._file.read_bytes()
        return self.message.encode("utf-8")

    def data(self) -> _NotificationData:
        """Return the data to send to the notification service."""
        return {
            "content": self._content(),
            "headers": self._headers(),
        }


class Notifier:
    """A notification service."""

    def __init__(
        self, topic: str, url: str = DEFAULT_NTFY_SERVER, timeout: int = 30
    ) -> None:
        self.topic: str = topic

        self.url: str = url
        self.timeout: int = timeout

        self.client = httpx.Client(base_url=url, timeout=timeout)

    def notify(
        self,
        *,
        message: str = "",
        title: str = "",
        priority: int = Priority.DEFAULT,
        tags: list[str] | None = None,
        email: str | None = None,
        file: str | Path | None = None,
    ) -> None:
        """Send a notification."""
        response = self.client.post(
            self.topic,
            **Notification(
                message=message,
                title=title,
                priority=priority,
                tags=tags or [],
                email=email,
                file=file,
            ).data(),
        )

        response.raise_for_status()

    def __call__(self, *args, **kwargs):
        self.notify(*args, **kwargs)

    def __del__(self) -> None:
        self.client.close()


class NoopNotifier(Notifier):
    """A notification service that does nothing."""

    def __init__(self, *args, **kwargs) -> None:  # noqa
        pass

    def notify(self, **kwargs) -> None:
        """Do nothing."""
        pass

    def __del__(self) -> None:
        pass

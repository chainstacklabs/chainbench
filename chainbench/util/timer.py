import time


class Timer:
    """Simple timer class to measure time between events."""

    _timer: dict = {}

    @classmethod
    def set_timer(cls, timer_id) -> None:
        """Set a timer with a given id."""
        cls._timer[timer_id] = time.time()

    @classmethod
    def get_time_diff(cls, timer_id) -> float:
        """Get the time difference between now and the timer with the given id."""
        return time.time() - cls._timer[timer_id]

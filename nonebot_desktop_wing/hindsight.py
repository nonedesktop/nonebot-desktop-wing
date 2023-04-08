from threading import Thread
from typing import Callable, Generic, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")

bgobject_log_func = print
"""Function for logging BackgroundObject info."""


class BackgroundObject(Generic[P, T]):
    def __init__(
        self,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> None:
        """
        A descriptor for running functions in background.
        """
        self._func = func
        self._thread = Thread(None, self._work, None, args, kwargs)
        self._thread.start()
        bgobject_log_func(
            f"[BackgroundObject] '{func.__module__}.{func.__name__}' is "
            f"running in background with {args=}, {kwargs=}"
        )

    def __get__(self, obj, objtype=None) -> T:
        return self.get()

    def _work(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self._value = self._func(*args, **kwargs)
        bgobject_log_func(
            f"[BackgroundObject] '{self._func.__module__}."
            f"{self._func.__name__}' is done with {args=}, {kwargs=}"
        )

    def get(self) -> T:
        self._thread.join()
        return self._value
from threading import Thread
from typing import IO, Callable, Generic, ParamSpec, TypeVar

T = TypeVar("T")
AnyStr_T = TypeVar("AnyStr_T", str, bytes)
P = ParamSpec("P")


class BackgroundObject(Generic[P, T]):
    """A descriptor for running functions in background."""
    def __init__(
        self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> None:
        """
        Initialize (start) a call in background.

        - func: `(P...) -> T`   - A callable to be called in background.
        - *args: `P.args`       - Positional args for the callable.
        - **kwargs: `P.kwargs`  - Keyword args for the callable.
        """
        self._func = func
        self._thread = Thread(None, self._work, None, args, kwargs)
        self._thread.start()
        # bgobject_log_func(
        #     f"[BackgroundObject] '{func.__module__}.{func.__name__}' is "
        #     f"running in background with {args=}, {kwargs=}"
        # )

    def __get__(self, obj, objtype=None) -> T:
        return self.get()

    def _work(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self._value = self._func(*args, **kwargs)
        # bgobject_log_func(
        #     f"[BackgroundObject] '{self._func.__module__}."
        #     f"{self._func.__name__}' is done with {args=}, {kwargs=}"
        # )

    def get(self) -> T:
        """Wait for value."""
        self._thread.join()
        return self._value


class RealtimeIOPipe(Generic[AnyStr_T]):
    def __init__(
        self, stream: IO[AnyStr_T], writer: Callable[[AnyStr_T], object]
    ) -> None:
        self.stream = stream
        self.thread = Thread(target=self._pull)
        self.writer = writer
        self.thread.start()

    def _pull(self) -> None:
        while True:
            try:
                self.writer(self.stream.read(1))
            except ValueError:
                break
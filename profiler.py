"""Lightweight async/sync function profiler with JSONL logging and thread-safe call tracking."""

import functools as functoolsProfilerProtected
import inspect as inspectProfilerProtected
import json as jsonProfilerProtected
import threading as threadingProfilerProtected
import datetime as datetimeProfilerProtected
import os as osProfilerProtected
import itertools
from typing import Callable, Any, Dict, Optional
import atexit as atexitProfilerProtected


class ProfilerState:
    """
    Singleton class that holds global state for the profiler:
    - Program start time
    - Log file handle
    - Lock for thread-safe writing
    - Unique call ID generator
    - Per-thread call stacks
    """

    _instance = None

    def __init__(self):
        """Initialize the singleton instance. Should only be called via ProfilerState.get()."""
        if ProfilerState._instance is not None:
            raise RuntimeError("Use ProfilerState.get() to access the singleton.")

        self.program_start_time = datetimeProfilerProtected.datetime.now()
        self.base_dir = osProfilerProtected.getenv(
            "PROFILER_BASE_DIR", osProfilerProtected.getcwd()
        )
        self.log_file_path = osProfilerProtected.path.join(
            self.base_dir, "profiler_log.jsonl"
        )
        self.log_file = open(self.log_file_path, "a", encoding="utf-8")
        self.lock = threadingProfilerProtected.Lock()
        self.call_id_generator = itertools.count(1)
        self.call_stack = threadingProfilerProtected.local()

    @classmethod
    def get(cls) -> "ProfilerState":
        """
        Return the singleton instance of the profiler state.
        Creates the instance on first access.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def close(self) -> None:
        """Close the log file. Registered to run automatically on program exit."""
        self.log_file.close()


def enter_function(function_name: str) -> Dict[str, Optional[int]]:
    """
    Push the current function onto the thread-local call stack
    and return the unique call ID and parent call ID (if any).

    Args:
        function_name: The fully-qualified name of the function being entered.

    Returns:
        Dictionary with `call_id` and `parent_call_id`.
    """
    state = ProfilerState.get()
    if not hasattr(state.call_stack, "stack"):
        state.call_stack.stack = []

    call_id = next(state.call_id_generator)
    parent_call_id = (
        state.call_stack.stack[-1]["call_id"] if state.call_stack.stack else None
    )

    state.call_stack.stack.append({"function": function_name, "call_id": call_id})

    return {"call_id": call_id, "parent_call_id": parent_call_id}


def exit_function() -> None:
    """
    Pop the most recent function from the thread-local call stack.
    Called automatically after the wrapped function returns.
    """
    state = ProfilerState.get()
    if hasattr(state.call_stack, "stack") and state.call_stack.stack:
        state.call_stack.stack.pop()


def log_record(record: list) -> None:
    """
    Append a profiling event record to the JSONL log file in a thread-safe way.

    Args:
        record: A list containing :
        [start(ms), duration(ms), function_name, call_id, parent_call_id, is_async (0/1)].
    """
    state = ProfilerState.get()
    with state.lock:
        state.log_file.write(jsonProfilerProtected.dumps(record) + "\n")


def profile(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that instruments both synchronous and asynchronous functions
    to log execution time, call hierarchy, and function metadata.

    Args:
        func: The function to wrap.

    Returns:
        A wrapped function that logs start time, duration, and parent-child relationships.
    """
    state = ProfilerState.get()

    if inspectProfilerProtected.iscoroutinefunction(func):

        @functoolsProfilerProtected.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapped async function with profiling."""
            context = enter_function(func.__qualname__)
            start_time = (
                datetimeProfilerProtected.datetime.now() - state.program_start_time
            )
            try:
                return await func(*args, **kwargs)
            finally:
                duration = (
                    datetimeProfilerProtected.datetime.now()
                    - state.program_start_time
                    - start_time
                )
                log_record(
                    [
                        round(start_time.total_seconds() * 1000, 4),
                        round(duration.total_seconds() * 1000, 4),
                        func.__qualname__,
                        context["call_id"],
                        context["parent_call_id"],
                        1,  # is_async
                    ]
                )
                exit_function()

        return async_wrapper

    @functoolsProfilerProtected.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapped sync function with profiling."""
        context = enter_function(func.__qualname__)
        start_time = datetimeProfilerProtected.datetime.now() - state.program_start_time
        try:
            return func(*args, **kwargs)
        finally:
            duration = (
                datetimeProfilerProtected.datetime.now()
                - state.program_start_time
                - start_time
            )
            log_record(
                [
                    round(start_time.total_seconds() * 1000, 4),
                    round(duration.total_seconds() * 1000, 4),
                    func.__qualname__,
                    context["call_id"],
                    context["parent_call_id"],
                    0,  # is_sync
                ]
            )
            exit_function()

    return sync_wrapper


def close_file() -> None:
    """
    Gracefully close the log file on program exit.
    Automatically registered with atexit.
    """
    ProfilerState.get().close()


# Register cleanup
atexitProfilerProtected.register(close_file)

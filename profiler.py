'''Main profiler code that will be injected'''
import functools as functoolsProfilerProtected
import inspect as inspectProfilerProtected
import json as jsonProfilerProtected
import threading as threadingProfilerProtected
import datetime as datetimeProfilerProtected
import os as osProfilerProtected
import itertools
from typing import Callable, Any, Dict, Optional
import atexit as atexitProfilerProtected


# Base directory to store the log file (default = current dir or env var override)
BASE_DIR: str = osProfilerProtected.getenv("PROFILER_BASE_DIR", osProfilerProtected.getcwd())
LOG_FILE: str = osProfilerProtected.path.join(BASE_DIR, "profiler_log.jsonl")
LOCK: threadingProfilerProtected.Lock = threadingProfilerProtected.Lock()

# Global unique call ID generator
CALL_ID_GENERATOR = itertools.count(1)

# Thread-local call stack per thread
CALL_STACK = threadingProfilerProtected.local()
CURR_LOG_GILE =  open(LOG_FILE, "a",encoding='utf-8')

PROGRAM_START_TIME = None

def enter_function(function_name: str) -> Dict[str, Optional[int]]:
    """
    Push current function onto thread-local call stack and return parent info.
    """
    if not hasattr(CALL_STACK, 'stack'):
        CALL_STACK.stack = []

    call_id = next(CALL_ID_GENERATOR)
    parent_call_id = CALL_STACK.stack[-1]['call_id'] if CALL_STACK.stack else None

    CALL_STACK.stack.append({
        'function': function_name,
        'call_id': call_id
    })

    return {'call_id': call_id, 'parent_call_id': parent_call_id}

def exit_function() -> None:
    """
    Pop current function from call stack.
    """
    if hasattr(CALL_STACK, 'stack') and CALL_STACK.stack:
        CALL_STACK.stack.pop()

def log_record(record: Dict[str, Any]) -> None:
    """
    Thread-safe log writer.
    """
    with LOCK:
        CURR_LOG_GILE.write(jsonProfilerProtected.dumps(record) + "\n")

def profile(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that wraps both synchronous and asynchronous functions
    to log start and end events with call instance tracking.
    """
    global PROGRAM_START_TIME
    if not PROGRAM_START_TIME:
        PROGRAM_START_TIME = datetimeProfilerProtected.datetime.now()
        
    if inspectProfilerProtected.iscoroutinefunction(func):
        @functoolsProfilerProtected.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            context = enter_function(func.__qualname__)
            start_time = datetimeProfilerProtected.datetime.now() - PROGRAM_START_TIME
            try:
                return await func(*args, **kwargs)
            finally:
                duration = datetimeProfilerProtected.datetime.now() - PROGRAM_START_TIME  - start_time
                log_record([
                     f'{start_time.total_seconds() * 1000:.4f}',
                     f'{duration.total_seconds() * 1000:.4f}',
                     func.__qualname__,
                     context['call_id'],
                     context['parent_call_id'],
                     1
                ])
                exit_function()

        return async_wrapper

    @functoolsProfilerProtected.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        context = enter_function(func.__qualname__)
        start_time = datetimeProfilerProtected.datetime.now() - PROGRAM_START_TIME
        try:
            return func(*args, **kwargs)
        finally:
            duration = datetimeProfilerProtected.datetime.now() - PROGRAM_START_TIME - start_time
            log_record([
                 f'{start_time.total_seconds() * 1000:.4f}',
                 f'{duration.total_seconds() * 1000:.4f}',
                 func.__qualname__,
                 context['call_id'],
                 context['parent_call_id'],
                 1
            ])
            exit_function()
    return sync_wrapper

def close_file():
    """handels file closing at the end of program"""
    CURR_LOG_GILE.close()


atexitProfilerProtected.register(close_file)

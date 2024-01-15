
import functools
import inspect
import os
import resource
import socket
from datetime import datetime
import threading
import uuid


def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        # fallback to __qualname__ parsing
        meth = getattr(meth, '__func__', meth)
    if inspect.isfunction(object=meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[
            0].rsplit('.', 1)[0],
            None)
        if isinstance(cls, type):
            return cls
    # handle special descriptor objects
    return getattr(meth, '__objclass__', None)


class ProfilingDecorators:
    HOST = os.environ.get('HOST', "127.0.0.1")
    PORT = int(os.environ.get('PORT', "65434"))

    def time_profile(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = datetime.now()
            val = func(*args, **kwargs)
            end = datetime.now()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ProfilingDecorators.HOST, ProfilingDecorators.PORT))
                s.sendall(bytes('time;'+str(uuid.uuid1()) + ';'+str(func.__name__) + ';' +
                          str(get_class_that_defined_method(meth=func))+';'+str(threading.get_ident())+';' + str(start) + ';'+str(end), 'utf-8'))
            return val
        return wrapper

    def memory_profile(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            val = func(*args, **kwargs)
            end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ProfilingDecorators.HOST, ProfilingDecorators.PORT))
                s.sendall(bytes('memory;'+str(uuid.uuid1()) + ';'+str(func.__name__) + ';' +
                          str(get_class_that_defined_method(func))+';' + str(threading.get_ident())+';' + str(start) + ';'+str(end), 'utf-8'))
            return val
        return wrapper


import os
import socket
from datetime import datetime
import uuid

class ProfilingDecorators:
    HOST = os.environ.get('HOST', "127.0.0.1") 
    PORT = int(os.environ.get('PORT', "65433") )
    
    def time_profile(func):
        def wrapper(*args, **kwargs):
            start = datetime.now()
            val = func(*args, **kwargs)
            end = datetime.now()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ProfilingDecorators.HOST, ProfilingDecorators.PORT))
                s.sendall(bytes('time;'+str(uuid.uuid1()) +';'+str(func.__name__) +';'+ str(start) + ';'+str(end), 'utf-8'))
            return val
        return wrapper
    
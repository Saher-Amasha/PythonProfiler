import os
import socket
from controller import Model

from logic.stamps.time_stamp import TimeStamp



class ProfilerServer:
    HOST = os.environ.get('HOST', "127.0.0.1") 
    PORT = int(os.environ.get('PORT', "65433") )
    @staticmethod
    def run():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ProfilerServer.HOST, ProfilerServer.PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        ProfilerServer.init_stamp_from_bytes(data)
                        if not data:
                            break
                        print(data)

    @staticmethod
    def init_stamp_from_bytes(data):
        split_desc_string = data.decode('utf-8').split(';')
        if len(split_desc_string) > 0 :
            match split_desc_string[0]:
                case 'time':
                    Model.add_time_stamp(split_desc_string[1],TimeStamp.init_from_bytes(split_desc_string[1:]))
                case 'mem':
                    # TODO FIX
                    Model.add_memmory_stamp(split_desc_string[1],TimeStamp.init_from_bytes(split_desc_string[1:]))
                    

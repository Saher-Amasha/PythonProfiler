from dataclasses import dataclass


@dataclass
class BaseStamp():
    """
    object that holds a time stap and additional info about the function
    """
    id:str
    name:str
    file_name:str
    thread_id:str
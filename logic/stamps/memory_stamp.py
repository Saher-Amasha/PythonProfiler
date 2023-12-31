from dataclasses import dataclass

from logic.stamps.base_stamp import BaseStamp


@dataclass
class MemoryStamp(BaseStamp):
    """
    object that holds a time stap and additional info about the function
    """
    start_memory:float
    end_memory:float

    @staticmethod
    def init_from_bytes(split_desc_string):
        """
        init date time from a string
        """
        if len(split_desc_string) > 0:

            id = split_desc_string[0]
            name = split_desc_string[1]
            start_memory = float(split_desc_string[2])
            end_memory = float(split_desc_string[3])

            return MemoryStamp(id=id,name=name,start_memory=start_memory,end_memory=end_memory)
    
    def __lt__(self, other):
        return self.end_memory  - self.start_memory < other.end_memory - other.start_memory
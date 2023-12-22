from dataclasses import dataclass
from datetime import datetime

from logic.stamps.base_stamp import BaseStamp


@dataclass
class TimeStamp(BaseStamp):
    """
    object that holds a time stap and additional info about the function
    """
    start:datetime
    end:datetime
    format:str ="%Y-%m-%d %H:%M:%S.%f"

    @staticmethod
    def init_from_bytes(split_desc_string):
        """
        init date time from a string
        """
        if len(split_desc_string) > 0:

            id = split_desc_string[0]
            name = split_desc_string[1]
            start = datetime.strptime(split_desc_string[2], TimeStamp.format)
            end = datetime.strptime(split_desc_string[3], TimeStamp.format)

            return TimeStamp(id=id,name=name,start=start,end=end)
    def __lt__(self, other):
        return self.start < other.start
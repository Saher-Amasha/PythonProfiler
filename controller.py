from datetime import datetime


class Model:
    TIME_STAMPS = dict()
    MEMORY_STAMPS = dict()
    START_TIME= datetime.now()
    @staticmethod
    def add_time_stamp(id,val):
        Model.TIME_STAMPS[id]= val
        # MainWindow.update()
    @staticmethod
    def add_memmory_stamp(id,val):
        Model.MEMORY_STAMPS[id]= val
        # MainWindow.update()
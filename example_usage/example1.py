import random
from time import sleep

from logic.profiling_meta import ProfilingMeta




class Example(metaclass=ProfilingMeta):

    @staticmethod
    def ex1_func():
        print("1")
        sleep(2)
        Example.ex2_func()
        sleep(3)
        print("2")

    @staticmethod
    def ex2_func():
        print("1")
        sleep(2)
        print("2")

    @staticmethod
    def ex3_func():
        print("1")
        sleep(random.randint(0,5))
        print("2")

    @staticmethod
    def test():
        i = 0 
        while i < 10 :
            sleep(random.randint(0,5))
            match random.randint(0,2):
                case 0:
                    Example.ex1_func()
                case 1:
                    Example.ex2_func()
                case 2:
                    Example.ex3_func()

            i+=1
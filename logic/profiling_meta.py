from logic.profiling_decorators import ProfilingDecorators

class ProfilingMeta(type):
    def __new__(cls, name, bases, class_dict):
        for key, value in class_dict.items():
            if callable(value):
                class_dict[key] = ProfilingDecorators.time_profile(ProfilingDecorators.memory_profile(value))
        return super().__new__(cls, name, bases, class_dict)

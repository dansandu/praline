from sys import modules
from logging import getLogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
from time import time
from functools import wraps


class Tracer:
    def __init__(self, level, parameters, tags, function, function_args, function_kwargs):
        self.logger = getLogger(modules[function.__module__].__name__)
        self.level = level
        self.parameters = parameters
        self.tags = tags
        self.function = function
        self.function_args = function_args
        self.function_kwargs = function_kwargs
        self.start_time = None
        self.return_value = None
        self.exception = None

    def __enter__(self):
        self.start_time = time()
        return self

    def trace(self):
        try:
            self.return_value = self.function(*self.function_args, **self.function_kwargs)
        except Exception as exception:
            self.exception = exception
            raise exception
        return self.return_value

    def __exit__(self, type, value, traceback):
        max_return_value_output = 2048
        metadata = {**self.tags}
        index = 0
        for value in self.function_args:
            argument = self.function.__code__.co_varnames[index]
            if self.parameters is None or argument in self.parameters:
                metadata[argument] = value
            index += 1
        metadata.update(self.function_kwargs)
        if not self.exception:
            return_value = str(self.return_value)
            return_value = return_value[:max_return_value_output] + '...' if len(return_value) > max_return_value_output else return_value
            self.logger.log(self.level, f"{self.function.__name__} {' '.join([k + '=' + repr(v) for k, v in metadata.items()])} -> {return_value} {time() - self.start_time}s")
        else:
            self.logger.critical(f"{self.function.__name__} {' '.join([k + '=' + repr(v) for k, v in metadata.items()])} raised {self.exception}")

def trace(_function=None, *, level=DEBUG, parameters=None, **tags):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with Tracer(level, parameters, tags, function, args, kwargs) as tracer:
                return tracer.trace()
        return wrapper

    if _function is None:
        return decorator
    else:
        return decorator(_function)

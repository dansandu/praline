from praline.common.tracing import trace

stages = {}


class Stage:
    def __init__(self, name, consumes, produces, cacheable, parameters, exposed, invoker):
        self.name = name
        self.consumes = consumes[:]
        self.produces = produces[:]
        self.cacheable = cacheable
        self.parameters = parameters[:]
        self.exposed = exposed
        self.invoker = invoker

    def __str__(self):
        return str(dict(name=self.name, consumes=self.consumes, produces=self.produces, cacheable=self.cacheable, parameters=self.parameters, exposed=self.exposed))

    def __repr__(self):
        return str(self)


def stage(_function=None, consumes=[], produces=[], exposed=False, cacheable=False, parameters=[]):
    def decorator(function):
        wrapped = trace(function)
        name = function.__name__
        if name in stages:
            raise RuntimeError(f"multiple definition of '{name}' stage")
        stages[name] = Stage(name, consumes, produces, cacheable, parameters, exposed, wrapped)
        return wrapped
    if _function is None:
        return decorator
    return decorator(_function)

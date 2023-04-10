from dataclasses import dataclass
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from praline.common.tracing import trace
from typing import Any, Callable, Dict, List


class StageNameConflictError(Exception):
    pass


@dataclass(frozen=True, repr=False)
class Stage:
    name              : str
    requirements      : List[List[str]]
    output            : List[str]
    predicate         : Callable[[FileSystem, Dict[str, Any], Dict[str, Any]], bool]
    program_arguments : List[Dict[str, Any]]
    cacheable         : bool
    exposed           : bool
    invoker           : Callable[[FileSystem, StageResources, Dict[str, Any], Dict[str, Any], Dict[str, Any], RemoteProxy, ProgressBarSupplier], None]

    def __str__(self):
        return f"Stage(name={self.name}, cacheable={self.cacheable}, exposed={self.exposed})"

    def __repr__(self):
        return f"Stage(name={self.name}, cacheable={self.cacheable}, exposed={self.exposed})"

registered_stages: Dict[str, Stage] = {}


def stage(_function         : Callable[[FileSystem, StageResources, Dict[str, Any], Dict[str, Any], Dict[str, Any], RemoteProxy, ProgressBarSupplier], None] = None,
          requirements      : List[List[str]] = [[]],
          output            : List[str] = [],
          predicate         : Callable[[FileSystem, Dict[str, Any], Dict[str, Any]], bool] = lambda _, __, ___: True,
          program_arguments : List[Dict[str, Any]] = [],
          cacheable         : bool = False,
          exposed           : bool = False):
    def decorator(function: Callable[[FileSystem, StageResources, Dict[str, Any], Dict[str, Any], Dict[str, Any], RemoteProxy, ProgressBarSupplier], None]):
        wrapped = trace(function, parameters=['resources', 'cache', 'program_arguments'])
        name = function.__name__
        if name in registered_stages:
            raise StageNameConflictError(f"multiple stage definitions named '{name}'")
        registered_stages[name] = Stage(name, requirements, output, predicate, program_arguments, cacheable, exposed, wrapped)
        return wrapped
    if _function is None:
        return decorator
    return decorator(_function)

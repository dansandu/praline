from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ArtifactManifest
from praline.common.compiling.compiler import CompilerWrapper
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from praline.common.tracing import trace

import pkgutil
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple


class StageNameConflictError(Exception):
    pass


@dataclass(frozen=True)
class StageArguments:
    file_system: FileSystem = None
    configuration: Dict[str, Any] = None
    program_arguments: Dict[str, Any] = None
    remote_proxy: RemoteProxy = None
    artifact_manifest: ArtifactManifest = None
    compiler: CompilerWrapper = None
    resources: StageResources = None
    cache: Dict[str, Any] = None
    progress_bar_supplier: ProgressBarSupplier = None


@dataclass(frozen=True)
class StagePredicateArguments:
    file_system: FileSystem = None
    configuration: Dict[str, Any] = None
    program_arguments: Dict[str, Any] = None
    remote_proxy: RemoteProxy = None
    artifact_manifest: ArtifactManifest = None
    compiler: CompilerWrapper = None


@dataclass(frozen=True)
class StagePredicateResult:
    can_run: bool
    explanation: str

    @staticmethod
    def success():
        return StagePredicateResult(can_run=True, explanation=None)
    
    @staticmethod
    def failure(explanation: str):
        return StagePredicateResult(can_run=False, explanation=explanation)


@dataclass(frozen=True)
class Stage:
    name             : str
    requirements     : List[List[str]]
    output           : List[str]
    predicate        : Callable[[StagePredicateArguments], StagePredicateResult]
    program_arguments: List[Dict[str, Any]]
    cacheable        : bool
    exposed          : bool
    invoker          : Callable[[StageArguments], None]


registered_stages = {}


def get_stages() -> Dict[str, Stage]:
    path = pkgutil.extend_path(__path__, __name__)
    for _, modname, _ in pkgutil.walk_packages(path=path, prefix=__name__ + '.'):
        __import__(modname)
    return registered_stages


def stage(_function        : Callable[[StageArguments], None] = None,
          requirements     : List[List[str]] = [[]],
          output           : List[str] = [],
          predicate        : Callable[[StagePredicateArguments], StagePredicateResult] = lambda _: StagePredicateResult.success(),
          program_arguments: List[Dict[str, Any]] = [],
          cacheable        : bool = False,
          exposed          : bool = False):
    def decorator(function: Callable[[StageArguments], None]):
        wrapped = trace(function, parameters=['resources', 'cache', 'program_arguments'])
        name = function.__name__
        if name in registered_stages:
            raise StageNameConflictError(f"multiple stage definitions named '{name}'")
        registered_stages[name] = Stage(name, 
                                        requirements,
                                        output, 
                                        predicate, 
                                        program_arguments,
                                        cacheable, 
                                        exposed, 
                                        wrapped)
        return wrapped
    if _function is None:
        return decorator
    return decorator(_function)

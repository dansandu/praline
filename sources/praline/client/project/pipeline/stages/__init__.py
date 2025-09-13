from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ArtifactManifest
from praline.common.exception import DirectUserMessageException, StageNameConflictException
from praline.common.project_structure import ProjectStructure
from praline.common.compiling.compiler import Compiler
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem

import pkgutil
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass(frozen=True)
class StageArguments:
    is_target_stage: bool = False
    file_system: FileSystem = None
    configuration: Dict[str, Any] = None
    program_arguments: Dict[str, Any] = None
    remote_proxy: RemoteProxy = None
    project_structure: ProjectStructure = None
    artifact_manifest: ArtifactManifest = None
    compiler: Compiler = None
    resources: StageResources = None
    cache: Dict[str, Any] = None
    progress_bar_supplier: ProgressBarSupplier = None

    def skipOrExceptionIf(self, condition, message, exception=DirectUserMessageException):
        if condition:
            if self.is_target_stage:
                raise exception(message)
            else:
                return True
        else:
            return False


@dataclass(frozen=True)
class Stage:
    name             : str
    requirements     : List[str]
    output           : List[str]
    program_arguments: List[Dict[str, Any]]
    exposed          : bool
    cacheable        : bool
    invoker          : Callable[[StageArguments], None]


registered_stages = {}


def get_stages() -> Dict[str, Stage]:
    path = pkgutil.extend_path(__path__, __name__)
    for _, modname, _ in pkgutil.walk_packages(path=path, prefix=__name__ + '.'):
        __import__(modname)
    return registered_stages


def stage(
    _function        : Callable[[StageArguments], None] = None,
    requirements     : List[str] = [],
    output           : List[str] = [],
    program_arguments: List[Dict[str, Any]] = [],
    exposed          : bool = False,
    cacheable        : bool = True
):
    def decorator(function: Callable[[StageArguments], None]):
        name = function.__name__
        if name in registered_stages:
            raise StageNameConflictException(f"Multiple stage definitions named '{name}'")
        registered_stages[name] = Stage(name, requirements, output, program_arguments, exposed, cacheable, function)
        return function

    if _function is None:
        return decorator
    return decorator(_function)

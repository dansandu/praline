from praline.common import ArtifactManifest, CompilerType
from praline.common.project_structure import ProjectStructure
from praline.common.compiling.base_msvc import BaseMsvcCompilingStrategy, BaseMsvcYieldDescriptor
from praline.common.compiling.compiler import ICompilingStrategy, ICompilingStrategySupplier, IYieldDescriptor
from praline.common.file_system import FileSystem

import logging


logger = logging.getLogger(__name__)


class MsvcCompilingStrategy(BaseMsvcCompilingStrategy):
    def __init__(self, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure):
        super().__init__(compiler_name='cl', 
                         skipWhichCheck=True, 
                         file_system=file_system, 
                         artifact_manifest=artifact_manifest,
                         project_structure=project_structure)
        

class MsvcCompilingStrategySupplier(ICompilingStrategySupplier):
    def get_type(self) -> CompilerType:
        return CompilerType.msvc

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return BaseMsvcYieldDescriptor()

    def instantiate(self, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure) -> ICompilingStrategy:
        return MsvcCompilingStrategy(file_system, artifact_manifest, project_structure)

from praline.common import ArtifactManifest, Compiler
from praline.common.compiling.base_msvc import BaseMsvcCompiler, BaseMsvcYieldDescriptor
from praline.common.compiling.compiler import ICompiler, ICompilerSupplier, IYieldDescriptor
from praline.common.file_system import FileSystem

import logging


logger = logging.getLogger(__name__)


class MsvcCompiler(BaseMsvcCompiler):
    def __init__(self, file_system: FileSystem, artifact_manifest: ArtifactManifest):
        super().__init__(compiler_name='cl', skipWhichCheck=True, file_system=file_system, artifact_manifest=artifact_manifest)
        

class MsvcCompilerSupplier(ICompilerSupplier):
    def get_name(self) -> Compiler:
        return Compiler.msvc

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return BaseMsvcYieldDescriptor()

    def instantiate_compiler(self, file_system: FileSystem, artifact_manifest: ArtifactManifest) -> ICompiler:
        return MsvcCompiler(file_system, artifact_manifest)

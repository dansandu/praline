from praline.common import ArtifactManifest, CompilerType, ExportedSymbols, Mode, Platform
from praline.common.project_structure import ProjectStructure
from praline.common.compiling.compiler import CompilerInstantionError, ICompilingStrategy, ICompilingStrategySupplier, IYieldDescriptor
from praline.common.file_system import basename, FileSystem
from typing import List

import logging


logger = logging.getLogger(__name__)


class ClangYieldDescriptor(IYieldDescriptor):
    def get_object(self, source_relative_path: str) -> str:
        return super().get_object(source_relative_path) + '.o'

    def get_executable(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.out'

    def get_library(self, artifact_identifier: str) -> str:
        return f'lib{artifact_identifier}.dylib'

    def get_library_interface(self, artifact_identifier: str) -> str:
        return None

    def get_symbols_table(self, artifact_identifier: str) -> str:
        return None


class ClangCompilingStrategy(ICompilingStrategy):
    def __init__(self, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure):
        self.file_system       = file_system
        self.artifact_manifest = artifact_manifest
        self.project_structure = project_structure

        if artifact_manifest.exported_symbols == ExportedSymbols.explicit:
            visibility = 'hidden'
        elif artifact_manifest.exported_symbols == ExportedSymbols.all:
            visibility = 'default'
        else:
            raise RuntimeError(f"unrecognized exported symbols '{artifact_manifest.exported_symbols}'")

        self.flags = [
            f'-fvisibility={visibility}', '-fPIC', '-pthread', '-std=c++23',
            '-Werror', '-Wall', '-Wextra',
            '-DPRALINE_EXPORT=__attribute__((visibility("default")))',
            '-DPRALINE_IMPORT=__attribute__((visibility("default")))'
        ]
        
        if artifact_manifest.mode == Mode.debug:
            self.flags.append('-g')
        elif artifact_manifest.mode == Mode.release:
            self.flags.append('-O3')            
        else:
            raise RuntimeError(f"unrecognized mode '{artifact_manifest.mode}'")

        if artifact_manifest.platform != Platform.darwin:
            raise CompilerInstantionError(
                f"the clang compiler cannot be used on the '{artifact_manifest.platform}' platform")
        
        if file_system.which('clang++') == None:
            raise CompilerInstantionError(f"the clang compiler could not find the clang++ executable in the PATH")

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return ClangYieldDescriptor()

    def preprocess(self, headers: List[str], source_path: str) -> bytes:
        status, stdout, stderror = self.file_system.execute(
            ['clang++', '-E', '-P', source_path] + 
            self.flags + 
            [f'-I{self.project_structure.sources_root}', f'-I{self.project_structure.external_headers_root}']
        )
        
        if stderror:
            logger.error(stderror.decode())
        if status != 0:
            raise RuntimeError(f"failed preprocessing source {source_path} -- process exited with status code {status}")
        return stdout

    def compile(self, headers: List[str], source_path: str, object_path: str):
        self.file_system.execute_and_fail_on_bad_return(
            ['clang++', '-o', object_path, '-c', source_path] + 
            self.flags + 
            [f'-I{self.project_structure.sources_root}', f'-I{self.project_structure.external_headers_root}']
        )

    def link_executable(self,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str):
        self.file_system.execute_and_fail_on_bad_return(
            ['clang++', '-o', executable, '-rpath', 
             '@executable_path/../libraries',
             '-rpath', '@executable_path/../external/libraries'] +
            self.flags + objects + 
            [f'-L{self.project_structure.external_libraries_root}'] +
            [f'-l{basename(lib)[3:-6]}' for lib in external_libraries]
        )

    def link_library(self,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str):
        self.file_system.execute_and_fail_on_bad_return(
            ['clang++', '-o', library, '-shared', '-install_name', f'@rpath/{basename(library)}'] + 
            self.flags + objects + 
            [f'-L{self.project_structure.external_libraries_root}'] +
            [f'-l{basename(lib)[3:-6]}' for lib in external_libraries]
        )


class ClangCompilingStrategySupplier(ICompilingStrategySupplier):
    def get_type(self) -> CompilerType:
        return CompilerType.clang

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return ClangYieldDescriptor()

    def instantiate(self, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure) -> ICompilingStrategy:
        return ClangCompilingStrategy(file_system, artifact_manifest, project_structure)

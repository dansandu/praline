from praline.common import ArtifactManifest, ArtifactPrefix, CompilerType, ExportedSymbols, Mode, Platform
from praline.common.project_structure import ProjectStructure
from praline.common.compiling.compiler import (
    ICompilingStrategy, ICompilingStrategySupplier, IYieldDescriptor
)
from praline.common.exception import (
    CompilationException, CompilerInstantionException, LinkingException,
    PreprocessingException, ProcessExecutionException
)
from praline.common.file_system import basename, FileSystem
from typing import List

import logging


logger = logging.getLogger(__name__)


class GccYieldDescriptor(IYieldDescriptor):
    def get_object(self, source_relative_path: str) -> str:
        return super().get_object(source_relative_path) + '.o'

    def get_executable_and_symbols_table(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.out', None

    def get_library_and_symbols_table(self, artifact_identifier: str) -> str:
        return f'lib{artifact_identifier}.so', None

    def get_library_interface(self, artifact_identifier: str) -> str:
        return None

    def get_executable_prefix(self, artifact_prefix: ArtifactPrefix) -> ArtifactPrefix:
        return artifact_prefix

    def get_library_prefix(self, artifact_prefix: ArtifactPrefix) -> ArtifactPrefix:
        return ArtifactPrefix(f'{artifact_prefix.scope}:lib{artifact_prefix.prefix}')


class GccCompilingStrategy(ICompilingStrategy):
    def __init__(self, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure):
        self.file_system       = file_system
        self.artifact_manifest = artifact_manifest
        self.project_structure = project_structure

        if artifact_manifest.exported_symbols == ExportedSymbols.explicit:
            visibility = 'hidden'
        elif artifact_manifest.exported_symbols == ExportedSymbols.all:
            visibility = 'default'
        else:
            raise CompilerInstantionException(f"Unrecognized exported symbols '{artifact_manifest.exported_symbols}'")

        self.flags = [
            f'-fvisibility={visibility}', '-fPIC', '-pthread', '-std=c++23',
            '-Werror', '-Wall', '-Wextra',
            '-DPRALINE_EXPORT=__attribute__((visibility("default")))',
            '-DPRALINE_IMPORT=__attribute__((visibility("default")))',
            f'-DPRALINE_SOURCES_ROOT="{self.project_structure.sources_root.replace('\\', '/')}"'
        ]

        self.extra_libraries = ['libstdc++_libbacktrace.so']

        if artifact_manifest.mode == Mode.debug:
            self.flags.extend(['-g', '-DDEBUG'])
        elif artifact_manifest.mode == Mode.release:
            self.flags.extend(['-O3', '-DNDEBUG'])
        else:
            raise CompilerInstantionException(f"Unrecognized mode '{artifact_manifest.mode}'")

        if artifact_manifest.platform != Platform.linux:
            raise CompilerInstantionException(f"The gcc compiler cannot be used on the '{artifact_manifest.platform}' platform")

        if file_system.which('g++') == None:
            raise CompilerInstantionException(f"The gcc compiler could not find the g++ executable in the PATH")

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return GccYieldDescriptor()

    def preprocess(self, headers: List[str], source_path: str, main_source: bool) -> bytes:
        include_paths = [
            f'-I{self.project_structure.main_sources_root}', 
            f'-I{self.project_structure.main_generated_sources_root}', 
            f'-I{self.project_structure.external_headers_root}'
        ]

        if not main_source:
            include_paths.extend([f'-I{self.project_structure.test_sources_root}'])
            include_paths.extend([f'-I{self.project_structure.test_generated_sources_root}'])

        status, stdout, stderror = self.file_system.execute(
            ['g++', '-E', '-P', source_path] +
            self.flags +
            include_paths
        )

        if  status != 0 or len(stderror) > 0:
            raise PreprocessingException(status, stderror)

        return stdout

    def compile(self, headers: List[str], source_path: str, object_path: str, main_source: bool):
        include_paths = [
            f'-I{self.project_structure.main_sources_root}',
            f'-I{self.project_structure.main_generated_sources_root}',
            f'-I{self.project_structure.external_headers_root}'
        ]

        if not main_source:
            include_paths.extend([f'-I{self.project_structure.test_sources_root}'])
            include_paths.extend([f'-I{self.project_structure.test_generated_sources_root}'])

        try:
            self.file_system.execute_and_fail_on_bad_return(
                ['g++', '-o', object_path, '-c', source_path] + self.flags + include_paths
            )
        except ProcessExecutionException as exception:
            raise CompilationException(exception.status, exception.stdout, exception.stderror)

    def link_executable(self,
                        objects: List[str],
                        libraries: List[str],
                        libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str):
        try:
            self.file_system.execute_and_fail_on_bad_return(
                ['g++', '-o', executable, '-Wl,-rpath,$ORIGIN/../libraries', '-Wl,-rpath,$ORIGIN/../external/libraries'] +
                self.flags + objects +
                [f'-L{self.project_structure.libraries_root}', f'-L{self.project_structure.external_libraries_root}'] +
                [f'-l{basename(lib)[3:-3]}' for lib in libraries] +
                [f'-l{basename(lib)[3:-3]}' for lib in self.extra_libraries]
            )
        except ProcessExecutionException as exception:
            raise LinkingException(exception.status, exception.stdout, exception.stderror)

    def link_library(self,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str):
        try:
            self.file_system.execute_and_fail_on_bad_return(
                ['g++', '-o', library, '-shared'] +
                self.flags + objects + 
                [f'-L{self.project_structure.external_libraries_root}'] +
                [f'-l{basename(lib)[3:-3]}' for lib in external_libraries] +
                [f'-l{basename(lib)[3:-3]}' for lib in self.extra_libraries]
            )
        except ProcessExecutionException as exception:
            raise LinkingException(exception.status, exception.stdout, exception.stderror)

class GccCompilingStrategySupplier(ICompilingStrategySupplier):
    def get_type(self) -> CompilerType:
        return CompilerType.gcc

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return GccYieldDescriptor()

    def instantiate(self, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure) -> ICompilingStrategy:
        return GccCompilingStrategy(file_system, artifact_manifest, project_structure)

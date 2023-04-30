from praline.common import (Architecture, ArtifactManifest, Compiler, ExportedSymbols, Mode, Platform,
                            get_artifact_logging_level_code)
from praline.common.compiling.compiler import ICompiler, CompilerInstantionError, CompilerSupplier, YieldDescriptor
from praline.common.file_system import basename, FileSystem, join
from typing import List

import logging


logger = logging.getLogger(__name__)


class GccYieldDescriptor(YieldDescriptor):    
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        return super().get_object(sources_root, objects_root, source) + '.o'

    def get_executable(self, executables_root, name: str) -> str:
        return join(executables_root, f'{name}.out')

    def get_library(self, libraries_root, name: str) -> str:
        return join(libraries_root,  f"lib{name}.so")

    def get_library_interface(self, libraries_interfaces_root: str, name: str) -> str:
        return None

    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        return None


class GccCompiler(ICompiler):
    def __init__(self, file_system: FileSystem, artifact_manifest: ArtifactManifest):
        self.file_system       = file_system
        self.artifact_manifest = artifact_manifest
        logging_level_code     = get_artifact_logging_level_code(artifact_manifest.artifact_logging_level)

        if artifact_manifest.exported_symbols == ExportedSymbols.explicit:
            visibility = 'hidden'
        elif artifact_manifest.exported_symbols == ExportedSymbols.all:
            visibility = 'default'
        else:
            raise RuntimeError(f"unrecognized exported symbols '{logging_level_code}'")

        self.flags = [f'-fvisibility={visibility}', '-fPIC', '-pthread', '-std=c++17',
                      '-Werror', '-Wall', '-Wextra',
                      '-DPRALINE_EXPORT=__attribute__((visibility("default")))',
                      '-DPRALINE_IMPORT=__attribute__((visibility("default")))',
                      f'-DPRALINE_LOGGING_LEVEL={logging_level_code}']
        
        if artifact_manifest.mode == Mode.debug:
            self.flags.append('-g')
        elif artifact_manifest.mode == Mode.release:
            self.flags.append('-O3')            
        else:
            raise RuntimeError(f"unrecognized mode '{artifact_manifest.mode}'")
        
        if artifact_manifest.platform != Platform.linux:
            raise CompilerInstantionError(
                f"the gcc compiler cannot be used on the '{artifact_manifest.platform}' platform")
        
        if file_system.which('g++') == None:
            raise CompilerInstantionError(f"the gcc compiler could not find the g++ executable in the PATH")

    def get_yield_descriptor(self) -> YieldDescriptor:
        return GccYieldDescriptor()

    def preprocess(self,
                   headers_root: str,
                   external_headers_root: str,
                   headers: List[str],
                   source: str) -> bytes:
        status, stdout, stderror = self.file_system.execute(['g++', '-E', '-P', source] + self.flags + 
                                                            [f'-I{headers_root}', f'-I{external_headers_root}'])
        if stderror:
            logger.error(stderror.decode())
        if status != 0:
            raise RuntimeError(f"failed preprocessing source {source} -- process exited with status code {status}")
        return stdout

    def compile(self,
                headers_root: str,
                external_headers_root: str,
                headers: List[str],
                source: str,
                object_: str):
        self.file_system.execute_and_fail_on_bad_return(['g++', '-o', object_, '-c', source] + self.flags + 
                                                        [f'-I{headers_root}', f'-I{external_headers_root}'])

    def link_executable(self,
                        external_libraries_root: str,
                        external_libraries_interfaces_root: str,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str):
        self.file_system.execute_and_fail_on_bad_return(['g++', '-o', executable,
                                                         '-Wl,-rpath,$ORIGIN/../libraries',
                                                         '-Wl,-rpath,$ORIGIN/../external/libraries'] +
                                                        self.flags + objects + [f'-L{external_libraries_root}'] +
                                                        [f'-l{basename(lib)[3:-3]}' for lib in external_libraries])

    def link_library(self,
                     external_libraries_root: str,
                     external_libraries_interfaces_root: str,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str):
        self.file_system.execute_and_fail_on_bad_return(['g++', '-o', library, '-shared'] +
                                                        self.flags + objects + [f'-L{external_libraries_root}'] +
                                                        [f'-l{basename(lib)[3:-3]}' for lib in external_libraries])


class GccCompilerSupplier(CompilerSupplier):
    def get_name(self) -> Compiler:
        return Compiler.gcc

    def get_yield_descriptor(self) -> YieldDescriptor:
        return GccYieldDescriptor()

    def instantiate_compiler(self, file_system: FileSystem, artifact_manifest: ArtifactManifest) -> ICompiler:
        return GccCompiler(file_system, artifact_manifest)

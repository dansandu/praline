from logging import getLogger
from praline.common.compiling.compiler import Compiler
from praline.common.compiling.yield_descriptor import YieldDescriptor
from praline.common.file_system import basename, directory_name, FileSystem, relative_path, get_separator, join
from typing import List


class DarwinClangYieldDescriptor(YieldDescriptor):
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        name = relative_path(source, sources_root).replace(get_separator(), '-').replace('.cpp', '.o')
        return join(objects_root, name)

    def get_executable(self, executables_root: str, name: str) -> str:
        return join(executables_root, f'{name}.out')

    def get_library(self, libraries_root: str, name: str) -> str:
        return join(libraries_root, f'lib{name}.dylib')

    def get_library_interface(self, libraries_interfaces_root: str, name: str) -> str:
        return None

    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        return None


class DarwinClangCompiler(Compiler):
    def __init__(self, file_system: FileSystem, architecture: str, platform: str, mode: str):
        self.file_system  = file_system
        self.architecture = architecture
        self.platform     = platform
        self.mode         = mode
        
        self.flags = ['-fvisibility=hidden', '-fPIC', '-pthread', '-std=c++17',
                      '-Werror', '-Wall', '-Wextra',
                      '-DPRALINE_EXPORT=__attribute__((visibility("default")))',
                      '-DPRALINE_IMPORT=__attribute__((visibility("default")))']
        
        if self.mode == 'debug':
            self.flags.append('-g')
        elif self.mode == 'release':
            self.flags.append('-O3')            
        else:
            raise RuntimeError(f"unrecognized compiler mode '{self.mode}'")

    def get_name(self) -> str:
        return 'clang'

    def get_architecture(self) -> str:
        return self.architecture

    def get_platform(self) -> str:
        return self.platform

    def get_mode(self) -> str:
        return self.mode

    def matches(self) -> bool:
        return self.file_system.which('clang++') != None and self.platform == 'darwin'

    def preprocess(self,
                   headers_root: str,
                   external_headers_root: str,
                   headers: List[str],
                   source: str) -> bytes:
        status, stdout, stderror = self.file_system.execute(['clang++', '-E', '-P', source] + self.flags + 
                                                            [f'-I{headers_root}', f'-I{external_headers_root}'])
        if stderror:
            getLogger(__name__).error(stderror.decode())
        if status != 0:
            raise RuntimeError(f"failed preprocessing source {source} -- process exited with status code {status}")
        return stdout

    def compile(self,
                headers_root: str,
                external_headers_root: str,
                headers: List[str],
                source: str,
                object_: str) -> None:
        self.file_system.execute_and_fail_on_bad_return(['clang++', '-o', object_, '-c', source] + self.flags + 
                                                        [f'-I{headers_root}', f'-I{external_headers_root}'])

    def link_executable(self,
                        external_libraries_root: str,
                        external_libraries_interfaces_root: str,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str) -> None:
        self.file_system.execute_and_fail_on_bad_return(['clang++', '-o', executable,
                                                         '-rpath', '@executable_path/../libraries',
                                                         '-rpath', '@executable_path/../external/libraries'] +
                                                        self.flags + objects + [f'-L{external_libraries_root}'] +
                                                        [f'-l{basename(external_library)[3:-6]}' for external_library in external_libraries])

    def link_library(self,
                     external_libraries_root: str,
                     external_libraries_interfaces_root: str,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str) -> None:
        self.file_system.execute_and_fail_on_bad_return(['clang++', '-o', library, '-shared', '-install_name', f'@rpath/{basename(library)}'] +
                                                        self.flags + objects + [f'-L{external_libraries_root}'] +
                                                        [f'-l{basename(external_library)[3:-6]}' for external_library in external_libraries])

    def get_yield_descriptor(self) -> YieldDescriptor:
        return DarwinClangYieldDescriptor()

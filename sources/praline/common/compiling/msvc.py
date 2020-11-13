from praline.common.compiling.compiler import Compiler
from praline.common.compiling.yield_descriptor import YieldDescriptor
from praline.common.file_system import directory_name, FileSystem, relative_path, get_separator, join
from praline.common.tracing import trace
from typing import List
import logging


logger = logging.getLogger(__name__)


compiler_flags  = ['/analyze-', '/permissive-', '/GS', '/RTC1', '/Gd', '/MDd', '/Z7', '/FC', '/Od', '/sdl', '/fp:precise',
                   '/EHsc', '/diagnostics:caret', '/errorReport:none', '/std:c++17', '/nologo', '/WX', '/W3', '/Gm-',
                    '/Zc:wchar_t', '/Zc:inline', '/Zc:forScope', '/Oy-', '/wd4251', '/D_DEBUG', '/D_CONSOLE', '/D_UNICODE',
                   '/DUNICODE', '/DPRALINE_EXPORT=__declspec(dllexport)', '/DPRALINE_IMPORT=__declspec(dllimport)']


linker_flags    = ['/DYNAMICBASE', '/DEBUG:FULL', '/NXCOMPAT', '/INCREMENTAL:NO', '/MANIFEST:NO', '/ERRORREPORT:NONE',
                   '/NOLOGO', '/TLBID:1', '/WX']


extra_libraries_interfaces = ['kernel32.lib', 'user32.lib', 'gdi32.lib', 'winspool.lib', 'comdlg32.lib', 'advapi32.lib',
                              'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'uuid.lib', 'odbc32.lib', 'odbccp32.lib']


def get_msvc_machine(architecture: str):
    if architecture == 'x32':
        return 'X86'
    elif architecture == 'x64':
        return 'X64'
    elif architecture == 'arm':
        return 'ARM'


def get_include_commands(headers_roots: List[str]):
    includes_commands = []
    for headers_root in headers_roots:
        includes_commands.append('/I')
        includes_commands.append(headers_root)
    return includes_commands


def get_environment_file(architecture):
    if architecture == 'x32':
        batfile = 'vcvars32.bat'
    elif architecture == 'x64':
        batfile = 'vcvars64.bat'
    else:
        raise RuntimeError(f"Unkown architecture '{architecture}'")
    return fr"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\{batfile}"


class MsvcYieldDescriptor(YieldDescriptor):
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        name = relative_path(source, sources_root).replace(get_separator(), '-').replace('.cpp', '.obj')
        return join(objects_root, name)

    def get_executable(self, executables_root: str, name: str) -> str:
        return join(executables_root, f'{name}.exe')

    def get_library(self, libraries_root: str, name: str) -> str:
        return join(libraries_root, f'{name}.dll')

    def get_library_interface(self, library_interfaces_root: str, name: str) -> str:
        return join(library_interfaces_root, f'{name}.lib')

    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        return join(symbols_tables_root, f'{name}.pdb')


class MsvcCompiler(Compiler):
    def __init__(self, file_system: FileSystem, architecture: str, platform: str, mode: str):
        self.file_system  = file_system
        self.architecture = architecture
        self.platform     = platform
        self.mode         = mode

    def get_name(self) -> str:
        return 'msvc'

    def get_architecture(self) -> str:
        return self.architecture

    def get_platform(self) -> str:
        return self.platform

    def get_mode(self) -> str:
        return self.mode

    def matches(self) -> bool:
        return self.file_system.exists(get_environment_file(self.architecture)) and self.platform == 'windows'

    def preprocess(self,
                   headers_root: str,
                   external_headers_root: str,
                   headers: List[str],
                   source: str) -> bytes:
        status, stdout, stderror = self.file_system.execute([get_environment_file(self.architecture), '>nul', '2>&1', '&&',
                                                             'cl', '/EP', source] + compiler_flags +
                                                            ['/I', headers_root, '/I', external_headers_root])
        if status != 0:
            logger.error(stderror.decode())
            raise RuntimeError(f"command exited with return code {status}")
        return stdout

    def compile(self,
                headers_root: str,
                external_headers_root: str,
                headers: List[str],
                source: str,
                object_: str) -> None:
        status, stdout, stderror = self.file_system.execute([get_environment_file(self.architecture), '>nul', '2>&1', '&&',
                                                             'cl', f'/Fo{object_}', '/c', source] + compiler_flags +
                                                            ['/I', headers_root, '/I', external_headers_root])
        if status != 0:
            logger.info(stdout.decode())
            logger.error(stderror.decode())
            raise RuntimeError(f"command exited with return code {status}")

    def link_executable(self,
                        external_libraries_root: str,
                        external_libraries_interfaces_root: str,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str) -> None:
        library_interface = executable.replace('.exe', '.lib')
        export_file = executable.replace('.exe', '.exp')
        status, stdout, stderror = self.file_system.execute([get_environment_file(self.architecture), '>nul', '2>&1', '&&',
                                                             'link', f'/OUT:{executable}',
                                                             f'/MACHINE:{get_msvc_machine(self.architecture)}',
                                                             f'/IMPLIB:{library_interface}', f'/PDB:{symbols_table}'] +
                                                            linker_flags + objects + extra_libraries_interfaces +
                                                            external_libraries_interfaces)
        if status != 0:
            logger.info(stdout.decode())
            logger.error(stderror.decode())
            raise RuntimeError(f"command exited with return code {status}")
        if self.file_system.exists(export_file):
            self.file_system.remove_file(export_file)
        if self.file_system.exists(library_interface):
            self.file_system.remove_file(library_interface)


    def link_library(self,
                     external_libraries_root: str,
                     external_libraries_interfaces_root: str,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str) -> None:
        export_file = library_interface.replace('.lib', '.exp')
        status, stdout, stderror = self.file_system.execute([get_environment_file(self.architecture), '>nul', '2>&1', '&&',
                                                             'link', f'/OUT:{library}', '/DLL', f'/IMPLIB:{library_interface}',
                                                             f'/MACHINE:{get_msvc_machine(self.architecture)}',
                                                             f'/PDB:{symbols_table}'] + linker_flags + objects +
                                                            extra_libraries_interfaces + external_libraries_interfaces)
        if status != 0:
            logger.info(stdout.decode())
            logger.error(stderror.decode())
            raise RuntimeError(f"command exited with return code {status}")
        if self.file_system.exists(export_file):
            self.file_system.remove_file(export_file)
        if not self.file_system.exists(library_interface):
            raise RuntimeError(f"no library interface file '{library_interface}' was created because there are no symbols to "
                               " export -- use PRALINE_EXPORT to export symbols")

    def get_yield_descriptor(self) -> YieldDescriptor:
        return MsvcYieldDescriptor()

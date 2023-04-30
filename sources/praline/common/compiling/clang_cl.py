from praline.common import (Architecture, ArtifactManifest, Compiler, ExportedSymbols, Mode, Platform, 
                            get_artifact_logging_level_code)
from praline.common.compiling.compiler import ICompiler, CompilerInstantionError, CompilerSupplier, YieldDescriptor
from praline.common.file_system import FileSystem, join
from typing import List

import logging


logger = logging.getLogger(__name__)


def get_msvc_machine(architecture: Architecture) -> str:
    if architecture == Architecture.x32:
        return 'X86'
    elif architecture == Architecture.x64:
        return 'X64'
    elif architecture ==Architecture.arm:
        return 'ARM'
    else:
        raise RuntimeError(f"unrecognized architecture '{architecture}'")


def get_environment_file(architecture: Architecture) -> str:
    if architecture == Architecture.x32:
        batfile = 'vcvars32.bat'
    elif architecture == Architecture.x64:
        batfile = 'vcvars64.bat'
    elif architecture ==Architecture.arm:
        batfile = 'vcvarsall.bat'
    else:
        raise RuntimeError(f"unrecognized architecture '{architecture}'")
    return fr"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\{batfile}"


class ClangClYieldDescriptor(YieldDescriptor):
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        return super().get_object(sources_root, objects_root, source) + '.obj'

    def get_executable(self, executables_root: str, name: str) -> str:
        return join(executables_root, f'{name}.exe')

    def get_library(self, libraries_root: str, name: str) -> str:
        return join(libraries_root, f'{name}.dll')

    def get_library_interface(self, library_interfaces_root: str, name: str) -> str:
        return join(library_interfaces_root, f'{name}.lib')

    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        return join(symbols_tables_root, f'{name}.pdb')


class ClangClCompiler(ICompiler):
    def __init__(self, file_system: FileSystem, artifact_manifest: ArtifactManifest):
        self.file_system       = file_system
        self.artifact_manifest = artifact_manifest
        self.environment_file  = get_environment_file(artifact_manifest.architecture)
        self.machine           = get_msvc_machine(artifact_manifest.architecture)
        logging_level_code     = get_artifact_logging_level_code(artifact_manifest.artifact_logging_level)
        
        self.compiler_flags  = ['/analyze-', '/permissive-', '/GS', '/Gd', '/FC', '/sdl', '/fp:precise',
                                '/EHsc', '/diagnostics:caret', '/errorReport:none', '/std:c++17', '/nologo', '/WX',
                                '/W3', '/Zc:wchar_t', '/Zc:inline', '/Zc:forScope', '/Oy-', '/wd4251', '/D_CONSOLE',
                                '/D_UNICODE', '/DUNICODE', '/DPRALINE_EXPORT=__declspec(dllexport)',
                                '/DPRALINE_IMPORT=__declspec(dllimport)',
                                f'-DPRALINE_LOGGING_LEVEL={logging_level_code}']

        self.linker_flags = ['/DYNAMICBASE', '/NXCOMPAT', '/INCREMENTAL:NO', '/MANIFEST:NO', '/ERRORREPORT:NONE',
                             '/NOLOGO', '/TLBID:1', '/WX']

        self.extra_libraries_interfaces = ['kernel32.lib', 'user32.lib', 'gdi32.lib', 'winspool.lib', 'comdlg32.lib', 
                                           'advapi32.lib', 'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'uuid.lib', 
                                           'odbc32.lib', 'odbccp32.lib']

        if artifact_manifest.mode == Mode.debug:
            self.compiler_flags.extend(['/MDd', '/RTC1', '/Z7', '/Od', '/D_DEBUG'])
            self.linker_flags.extend(['/DEBUG:FULL'])
        elif artifact_manifest.mode == Mode.release:
            self.compiler_flags.extend(['/MD', '/O2', '/DNDEBUG'])
            self.linker_flags.extend(['/DEBUG:NONE'])
        else:
            raise RuntimeError(f"unrecognized mode '{self.mode}'")

        if artifact_manifest.platform != Platform.windows:
            raise CompilerInstantionError(f"the clang-cl compiler does not support the '{artifact_manifest.platform}' platform")
        
        if not file_system.exists(self.environment_file):
            raise CompilerInstantionError(f"the clang-cl compiler could not find environment configuration batch file")

        if file_system.which('clang-cl') == None:
            raise CompilerInstantionError(f"the clang-cl compiler could not find the clang-cl executable in the PATH")

        if artifact_manifest.exported_symbols == ExportedSymbols.all:
            raise CompilerInstantionError(f"the clang-cl compiler does not support currently exporting all symbols")

    def get_yield_descriptor(self) -> YieldDescriptor:
        return ClangClYieldDescriptor()

    def preprocess(self,
                   headers_root: str,
                   external_headers_root: str,
                   headers: List[str],
                   source: str) -> bytes:
        status, stdout, stderror = self.file_system.execute([self.environment_file, '>nul', '2>&1', '&&',
                                                             'clang-cl', '/EP', source] + self.compiler_flags +
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
        status, stdout, stderror = self.file_system.execute([self.environment_file, '>nul', '2>&1', '&&', 
                                                             'clang-cl', f'/Fo{object_}', '/c', source] + 
                                                            self.compiler_flags +
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
        library_interface = executable[:-4] + '.lib'
        export_file       = executable[:-4] + '.exp'
        status, stdout, stderror = self.file_system.execute([self.environment_file, '>nul', '2>&1', '&&', 
                                                             'lld-link', f'/OUT:{executable}',
                                                             f'/MACHINE:{self.machine}',
                                                             f'/IMPLIB:{library_interface}', 
                                                             f'/PDB:{symbols_table}'] + self.linker_flags + objects +
                                                            self.extra_libraries_interfaces +
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
        export_file = library_interface[:-4] + '.exp'
        status, stdout, stderror = self.file_system.execute([self.environment_file, '>nul', '2>&1', '&&',
                                                             'lld-link', f'/OUT:{library}', '/DLL', 
                                                             f'/IMPLIB:{library_interface}',
                                                             f'/MACHINE:{self.machine}',
                                                             f'/PDB:{symbols_table}'] + self.linker_flags + objects +
                                                            self.extra_libraries_interfaces + 
                                                            external_libraries_interfaces)
        if status != 0:
            logger.info(stdout.decode())
            logger.error(stderror.decode())
            raise RuntimeError(f"command exited with return code {status}")
        if self.file_system.exists(export_file):
            self.file_system.remove_file(export_file)
        if not self.file_system.exists(library_interface):
            logger.warn(f"no library interface file '{library_interface}' was created because there are no symbols to"
                        "export -- use PRALINE_EXPORT to export symbols")


class ClangClCompilerSupplier(CompilerSupplier):
    def get_name(self) -> Compiler:
        return Compiler.clang_cl

    def get_yield_descriptor(self) -> YieldDescriptor:
        return ClangClYieldDescriptor()

    def instantiate_compiler(self, file_system: FileSystem, artifact_manifest: ArtifactManifest) -> ICompiler:
        return ClangClCompiler(file_system, artifact_manifest)

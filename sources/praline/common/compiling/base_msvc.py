from praline.common import Architecture, ArtifactManifest, ExportedSymbols, Mode, Platform
from praline.common.project_structure import ProjectStructure
from praline.common.compiling.compiler import (
    CompilationError, CompilerInstantionError, ICompilingStrategy, 
    IYieldDescriptor, LinkingError, PreprocessingError
)
from praline.common.file_system import FileSystem, join, directory_name
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
        raise RuntimeError(f"Unrecognized architecture '{architecture}'")


def get_environment_file(architecture: Architecture) -> str:
    if architecture == Architecture.x32:
        batfile = 'vcvars32.bat'
    elif architecture == Architecture.x64:
        batfile = 'vcvars64.bat'
    elif architecture ==Architecture.arm:
        batfile = 'vcvarsall.bat'
    else:
        raise RuntimeError(f"Unrecognized architecture '{architecture}'")
    return fr"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\{batfile}"


class BaseMsvcYieldDescriptor(IYieldDescriptor):
    def get_object(self, source_relative_path: str) -> str:
        return super().get_object(source_relative_path) + '.obj'

    def get_executable(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.exe'

    def get_library(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.dll'

    def get_library_interface(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.lib'

    def get_symbols_table(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.pdb'


class BaseMsvcCompilingStrategy(ICompilingStrategy):
    def __init__(self, compiler_name: str, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure):
        self.compiler_name     = compiler_name
        self.file_system       = file_system
        self.artifact_manifest = artifact_manifest
        self.project_structure = project_structure
        self.environment_file  = get_environment_file(artifact_manifest.architecture)
        self.machine           = get_msvc_machine(artifact_manifest.architecture)
        
        self.compiler_flags  = [
            '/analyze-', '/permissive-', '/GS', '/Gd', '/FC', '/sdl', '/fp:precise',
            '/EHsc', '/diagnostics:caret', '/errorReport:none', '/std:c++latest', '/nologo', '/WX',
            '/W3', '/Zc:wchar_t', '/Zc:inline', '/Zc:forScope', '/Oy-', '/wd4251', '/D_CONSOLE',
            '/D_UNICODE', '/DUNICODE', '/DPRALINE_EXPORT=__declspec(dllexport)',
            '/DPRALINE_IMPORT=__declspec(dllimport)'
        ]

        self.linker_flags = [
            '/DYNAMICBASE', '/NXCOMPAT', '/INCREMENTAL:NO', '/MANIFEST:NO', '/ERRORREPORT:NONE',
            '/NOLOGO', '/TLBID:1', '/WX'
        ]

        self.extra_libraries_interfaces = [
            'kernel32.lib', 'user32.lib', 'gdi32.lib', 'winspool.lib', 'comdlg32.lib', 
            'advapi32.lib', 'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'uuid.lib', 
            'odbc32.lib', 'odbccp32.lib', 'ws2_32.lib'
        ]

        if artifact_manifest.mode == Mode.debug:
            self.compiler_flags.extend(['/MDd', '/RTC1', '/Z7', '/Od', '/D_DEBUG'])
            self.linker_flags.extend(['/DEBUG:FULL'])
        elif artifact_manifest.mode == Mode.release:
            self.compiler_flags.extend(['/MD', '/O2', '/DNDEBUG'])
            self.linker_flags.extend(['/DEBUG:NONE'])
        else:
            raise RuntimeError(f"Unrecognized mode '{self.mode}'")

        if artifact_manifest.platform != Platform.windows:
            raise CompilerInstantionError(f"The {compiler_name} compiler does not support the '{artifact_manifest.platform}' platform")

        if not file_system.exists(self.environment_file):
            raise CompilerInstantionError(f"The {compiler_name} compiler could not find environment configuration batch file")

        if compiler_name != 'cl' and file_system.which(compiler_name) == None:
            raise CompilerInstantionError(f"The {compiler_name} compiler could not find the {compiler_name} executable in the PATH")

        if artifact_manifest.exported_symbols == ExportedSymbols.all:
            raise CompilerInstantionError(f"The {compiler_name} compiler does not support currently exporting all symbols")

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return BaseMsvcYieldDescriptor()

    def preprocess(self, headers: List[str], source_path: str, main_source: bool) -> bytes:
        include_paths = ['/I', self.project_structure.main_sources_root, '/I', self.project_structure.external_headers_root]
        if not main_source:
            include_paths.extend(['/I', self.project_structure.test_sources_root])

        status, stdout, stderror = self.file_system.execute(
            [self.environment_file, '>nul', '2>&1', '&&', self.compiler_name, '/EP', source_path] + 
            self.compiler_flags + 
            include_paths
        )

        if  status != 0 or (self.compiler_name != 'cl' and len(stderror) > 0):
            raise PreprocessingError(status, stderror)

        return stdout

    def compile(self, headers: List[str], source_path: str, object_path: str, main_source: bool) -> None:
        include_paths = ['/I', self.project_structure.main_sources_root, '/I', self.project_structure.external_headers_root]
        if not main_source:
            include_paths.extend(['/I', self.project_structure.test_sources_root])

        status, stdout, stderror = self.file_system.execute(
            [self.environment_file, '>nul', '2>&1', '&&', self.compiler_name, f'/Fo{object_path}', '/c', source_path] + 
            self.compiler_flags +
            include_paths
        )

        if  status != 0 or len(stderror) > 0:
            raise CompilationError(status, stdout, stderror)

    def link_executable(self,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str) -> None:
        library_interface = executable[:-4] + '.lib'
        export_file       = executable[:-4] + '.exp'

        output_directory = directory_name(executable)
        link_executable_rsp_file = join(output_directory, 'link_executable.rsp')

        link_executable_arguments = ' '.join(
            [
                f'/OUT:{executable}',
                f'/MACHINE:{self.machine}',
                f'/IMPLIB:{library_interface}', 
                f'/PDB:{symbols_table}'
            ] +
            self.linker_flags +
            objects +
            self.extra_libraries_interfaces +
            external_libraries_interfaces
        )

        with self.file_system.open_file(link_executable_rsp_file, 'w') as f:
            f.write(link_executable_arguments)

        status, stdout, stderror = self.file_system.execute(
            [self.environment_file, '>nul', '2>&1', '&&', 'lld-link', f'@{link_executable_rsp_file}']
        )
        
        if  status != 0 or len(stderror) > 0:
            raise LinkingError(status, stdout, stderror)
        
        if self.file_system.exists(export_file):
            self.file_system.remove_file(export_file)
        
        if self.file_system.exists(library_interface):
            self.file_system.remove_file(library_interface)


    def link_library(self,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str) -> None:
        export_file = library_interface[:-4] + '.exp'

        output_directory = directory_name(library)
        link_library_rsp_file = join(output_directory, 'link_library.rsp')

        link_library_arguments = ' '.join(
            [
                f'/OUT:{library}', '/DLL', 
                f'/IMPLIB:{library_interface}',
                f'/MACHINE:{self.machine}',
                f'/PDB:{symbols_table}'
            ] + 
            self.linker_flags + 
            objects +
            self.extra_libraries_interfaces + 
            external_libraries_interfaces
        )

        with self.file_system.open_file(link_library_rsp_file, 'w') as f:
            f.write(link_library_arguments)

        status, stdout, stderror = self.file_system.execute(
            [self.environment_file, '>nul', '2>&1', '&&', 'lld-link', f'@{link_library_rsp_file}']
        )

        if  status != 0 or len(stderror) > 0:
            raise LinkingError(status, stdout, stderror)
        
        if self.file_system.exists(export_file):
            self.file_system.remove_file(export_file)
        
        if not self.file_system.exists(library_interface):
            logger.warn(f"No library interface file '{library_interface}' was created because there are no symbols to"
                        "export -- use PRALINE_EXPORT to export symbols")

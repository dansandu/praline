from logging import getLogger
from praline.common.compiler.base import Compiler
from praline.common.file_system import basename, directory_name, execute, execute_and_fail_on_bad_return

flags = ['-fPIC', '-pthread', '-O3', '-std=c++17', '-Werror', '-Wall', '-Wextra', '-Wno-literal-suffix']


class GccCompiler(Compiler):
    def name(self):
        return 'gcc'

    def executable(self):
        return 'g++'

    def allowed_platforms(self):
        return ['linux', 'windows']

    def preprocess(self, source, header_roots, headers):
        status, stdout, stderror = execute([self.executable(), '-E', '-P', source] + flags + 
                                           ['-I' + headers_root for headers_root in header_roots])
        if stderror:
            getLogger(__name__).error(stderror.decode())
        if status != 0:
            raise RuntimeError(f"failed preprocessing source {source} -- process exited with status code {status}")
        return stdout

    def compile(self, source, object_, headers_roots, headers):
        execute_and_fail_on_bad_return([self.executable(), '-o', object_, '-c', source] + flags + 
                                       ['-I' + headers_root for headers_root in headers_roots])

    def link_executable(self, executable, objects, external_libraries):
        external_libraries_paths = set([directory_name(external_library) for external_library in external_libraries])
        execute_and_fail_on_bad_return([self.executable(), '-o', executable,
                                        '-Wl,-rpath,$ORIGIN/../libraries',
                                        '-Wl,-rpath,$ORIGIN/../external/libraries'] +
                                       flags + objects + 
                                       [f'-L{external_libraries_path}' for external_libraries_path in external_libraries_paths] +
                                       [f'-l:{basename(external_library)}' for external_library in external_libraries])

    def link_library(self, library, objects, external_libraries):
        external_libraries_paths = set([directory_name(library) for library in external_libraries])
        execute_and_fail_on_bad_return([self.executable(), '-o', library, '-shared'] +
                                       flags + objects +
                                       [f'-L{external_libraries_path}' for external_libraries_path in external_libraries_paths] +
                                       [f'-l:{basename(external_library)}' for external_library in external_libraries])

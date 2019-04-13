from logging import getLogger
from praline.common.compiler.base import Compiler
from praline.common.file_system import basename, execute, execute_and_fail_on_bad_return

flags = ['-fPIC', '-pthread', '-O3', '-std=c++17', '-Werror', '-Wall', '-Wextra']


class DarwinClangCompiler(Compiler):
    def name(self):
        return 'clang'

    def executable(self):
        return 'clang++'

    def allowed_platforms(self):
        return ['darwin']

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
        execute_and_fail_on_bad_return([self.executable(), '-o', executable,
                                        '-rpath', '@executable_path/../libraries',
                                        '-rpath', '@executable_path/../external/libraries'] +
                                       flags + objects + external_libraries)

    def link_library(self, library, objects, external_libraries):
        execute_and_fail_on_bad_return([self.executable(), '-o', library, '-shared', '-install_name', f'@rpath/{basename(library)}'] +
                                       flags + objects + external_libraries)

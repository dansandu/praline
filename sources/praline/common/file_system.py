import os
import os.path
import platform
import shutil
import subprocess
import sys
import tarfile
from logging import getLogger
from praline.common.tracing import trace, INFO
from typing import Any, IO, List


logger = getLogger(__name__)


def directory_name(path : str) -> str:
    return os.path.dirname(path)


def join(path: str, *paths: str) -> str:
    return os.path.join(path, *paths)


def relative_path(path: str, start: str) -> str:
    return os.path.relpath(path, start)


def get_separator() -> str:
    return os.path.sep


def basename(path: str) -> str:
    return os.path.basename(path)


def normalized_path(path: str) -> str:
    return os.path.normpath(path)


def common_path(paths: List[str]) -> str:
    return os.path.commonpath(paths)


class FileSystem:
    @trace
    def execute(self, command: List[str], add_to_library_path: List[str] = [], interactive: bool = False) -> None:
        environment_copy = dict(os.environ)
        if add_to_library_path:
            if sys.platform == 'linux' or sys.platform == 'darwin':
                environment_copy['LD_LIBRARY_PATH'] = os.pathsep + os.pathsep.join(add_to_library_path)
            elif sys.platform == 'win32':
                environment_copy['PATH'] += os.pathsep + os.pathsep.join(add_to_library_path)
            else:
                raise RuntimeError(f"couldn't change library path -- unsupported platform '{sys.platform}'")
        
        if interactive:
            process = subprocess.Popen(command, shell=(os.name == 'nt'), env=environment_copy)
            process.wait()
            return process.returncode
        else:
            process = subprocess.Popen(command, shell=(os.name == 'nt'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment_copy)
            stdout, stderror = process.communicate()
            return process.returncode, stdout, stderror

    def execute_and_fail_on_bad_return(self, command: List[str], add_to_library_path: List[str] = [], interactive: bool = False) -> None:
        if interactive:
            status = self.execute(command, add_to_library_path=add_to_library_path, interactive=True)
        else:
            status, stdout, stderror = self.execute(command, add_to_library_path=add_to_library_path)
            if stdout:
                logger.info(stdout.decode())
            if stderror:
                logger.error(stderror.decode())
        
        if status != 0:
            raise RuntimeError(f"command exited with return code {status}")

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def is_file(self, path: str) -> bool:
        return os.path.isfile(path)

    def is_directory(self, path: str) -> bool:
        return os.path.isdir(path)

    def create_file_if_missing(self, path: str, contents: str = '') -> None:
        if not os.path.exists(path):
            logger.debug(f"creating file '{path}'")
            os.makedirs(name=directory_name(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(contents)
        elif not self.is_file(path):
            raise RuntimeError(f"'{path}' already exists and is not a file")

    def create_directory_if_missing(self, path: str) -> None:
        if not self.exists(path):
            logger.debug(f"creating directory '{path}'")
            os.makedirs(path)
        elif not self.is_directory(path):
            raise RuntimeError(f"'{path}' already exists and is not a directory")

    def list_directory(self, directory: str, hidden: bool = False) -> List[str]:
        return [entry for entry in os.scandir(directory) if hidden or not entry.name.startswith('.')]

    def files_in_directory(self, directory: str, hidden: bool = False) -> List[str]:
        return [join(r, f) for r, _, files in os.walk(directory) for f in files if hidden or not f.startswith('.')]

    def open_file(self, path: str, mode: str) -> IO[Any]:
        return open(path, mode)

    def get_working_directory(self) -> str:
        return os.getcwd()

    @trace
    def remove_directory_recursively(self, directory: str) -> None:
        shutil.rmtree(directory)

    @trace
    def remove_file(self, path) -> None:
        os.remove(path)

    def which(self, thing: str) -> str:
        directories = os.environ["PATH"].split(os.pathsep)
        current = directory_name(thing)
        if current:
            directories.append(current)
        for directory in directories:
            if self.exists(directory):
                for entry in os.scandir(directory):
                    path = join(directory, entry.name)
                    if thing == os.path.splitext(entry.name)[0] and os.access(path, os.X_OK) and entry.is_file():
                        return entry.path
        return None

    def get_architecture(self) -> str:
        m = platform.machine()
        if m == 'i386':
            return 'x32'
        elif m == 'AMD64' or m == 'x86_64':
            return 'x64'
        else:
            raise RuntimeError(f"unrecognized architecture {m}")

    def get_platform(self) -> str:
        return str(platform.system()).lower()

    def open_tarfile(self, path: str, mode: str):
        return tarfile.open(path, mode)

    def copyfileobj(self, source, destination):
        shutil.copyfileobj(source, destination)

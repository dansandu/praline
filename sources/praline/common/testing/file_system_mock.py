from dataclasses import dataclass
from typing import Any, Callable, Dict, IO, List, Set
import io
import os
import os.path
import pickle


@dataclass
class DirEntryMock:
    name: str
    path: str
    isfile: bool
    isdir: bool

    def is_file(self):
        return self.isfile

    def is_dir(self):
        return self.isdir


class FileMock(io.BytesIO):
    def __init__(self, contents: bytes, on_close: Callable[[Any], None]):
        super(FileMock, self).__init__(contents)
        self.on_close = on_close

    def __exit__(self, type, value, traceback):
        self.on_close(self)
        super(FileMock, self).__exit__(type, value, traceback)


class ArchiveMemberMock:
    def __init__(self, name: str, contents: bytes):
        self.name     = name
        self.contents = contents

    def isfile(self) -> bool:
        return True


class ArchiveMock:
    def __init__(self, members: Dict[str, bytes]):
        self.file_system = None
        self.members     = members
        self.on_close    = None

    def __enter__(self):
        return self

    def getmembers(self) -> List[ArchiveMemberMock]:
        return [ArchiveMemberMock(name, contents) for name, contents in self.members.items()]

    def add(self, file_path: str, archive_file_path: str) -> ArchiveMemberMock:
        with self.file_system.open_file(file_path, 'rb') as f:
            self.members[archive_file_path] = contents = f.read()
            return ArchiveMemberMock(archive_file_path, contents)

    def extract(self, member, extraction_path):
        path = os.path.join(extraction_path, member.name)
        with self.file_system.open_file(path, 'wb') as f:
            f.write(member.contents)

    def extractfile(self, archive_file_path: str):
        def on_close(file: FileMock):
            self.members[archive_file_path] = file.getvalue()

        return FileMock(self.members[archive_file_path], on_close)

    def __exit__(self, type, value, traceback):
        self.on_close(self)


def is_subpath(sub: str, path: str):
    sub_split = sub.split(os.sep)
    path_split = path.split(os.sep)
    return len(sub_split) < len(path_split) and sub_split[0: len(sub_split)] == path_split[0: len(sub_split)]


def is_subpath_or_path(sub: str, path: str):
    sub_split = sub.split(os.sep)
    path_split = path.split(os.sep)
    return len(sub_split) <= len(path_split) and sub_split[0: len(sub_split)] == path_split[0: len(sub_split)]


def unique_directories(directories: Set[str]):
    return {d for d in directories if all(not is_subpath(d, dd) for dd in directories)}


class FileSystemMock:
    def __init__(self,
                 directories: set = set(),
                 files: Dict[str, bytes] = {},
                 architecture: str = 'x64',
                 platform: str = 'linux',
                 working_directory: str = None,
                 on_which: Callable[[str], str] = None,
                 on_execute: Callable[[List[str], List[str], bool, Dict[str, str]], bool] = None):
        self.directories = unique_directories({os.path.normpath(p) for p in directories})
        self.files       = {}
        for path, contents in files.items():
            normalized_path = os.path.normpath(path)
            for directory_path in self.directories:
                if is_subpath_or_path(normalized_path, directory_path):
                    raise RuntimeError(f"cannot create file '{normalized_path}' -- '{directory_path}' is a directory")
            directory = os.path.dirname(normalized_path)
            if directory and not self.is_directory(directory):
                raise RuntimeError(f"directory '{directory}' doesn't exist")
            if self.exists(normalized_path):
                raise RuntimeError(f"cannot create file '{normalized_path}' -- it already exists")
            self.files[normalized_path] = contents
        
        self.open_files        = set()
        self.architecture      = architecture
        self.platform          = platform
        self.working_directory = os.path.normpath(working_directory) if working_directory else None
        self.on_which          = on_which
        self.on_execute        = on_execute
        self.stdout            = io.StringIO("")

    def execute_and_fail_on_bad_return(self,
                                       command: List[str], 
                                       add_to_library_path: List[str] = [], 
                                       interactive: bool = False, 
                                       add_to_env: Dict[str, str] = {}) -> None:
        if not self.on_execute(command, add_to_library_path, interactive, add_to_env):
            raise RuntimeError("command exited with failure")

    def get_working_directory(self) -> str:
        return self.working_directory

    def get_architecture(self) -> str:
        return self.architecture

    def get_platform(self) -> str:
        return self.platform

    def which(self, thing: str) -> str:
        return self.on_which(thing)

    def is_file(self, path: str) -> bool:
        normalized_path = os.path.normpath(path)
        return normalized_path in self.files

    def is_directory(self, path: str) -> bool:
        normalized_path = os.path.normpath(path)
        return any(is_subpath_or_path(normalized_path, d) for d in self.directories)

    def exists(self, path: str) -> bool:
        return self.is_file(path) or self.is_directory(path)

    def list_directory(self, directory: str, hidden: bool = False) -> List[str]:
        normalized_path = os.path.normpath(directory)
        directories     = {os.path.relpath(p, normalized_path).split(os.sep)[0]: p for p in self.directories if is_subpath(normalized_path, p)}
        files           = {os.path.basename(p) : p for p in self.files if os.path.dirname(p) == normalized_path}
        entries         = [DirEntryMock(n, d, False, True) for n, d in directories.items()] + [DirEntryMock(n, d, True, False) for n, d in files.items()]
        return [entry for entry in entries if hidden or not entry.name.startswith('.')]

    def files_in_directory(self, directory: str, hidden: bool = False) -> List[str]:
        normalized_path = os.path.normpath(directory)
        return [f for f in self.files if is_subpath(normalized_path, f) and (hidden or not f.startswith('.'))]

    def create_directory_if_missing(self, path: str) -> None:
        normalized_path = os.path.normpath(path)
        for file_path in self.files:
            if is_subpath_or_path(file_path, normalized_path):
                raise RuntimeError(f"cannot create directory '{normalized_path}' -- '{file_path}' is a file")
        if not self.is_directory(normalized_path):
            self.directories.add(normalized_path)
            self.directories = unique_directories(self.directories)

    def create_file_if_missing(self, path: str, contents = b'') -> None:
        normalized_path = os.path.normpath(path)
        for directory_path in self.directories:
            if is_subpath_or_path(normalized_path, directory_path):
                raise RuntimeError(f"cannot create file '{normalized_path}' -- '{directory_path}' is a directory")
        directory = os.path.dirname(normalized_path)
        if directory:
            self.create_directory_if_missing(directory)
        if normalized_path not in self.files:
            self.files[normalized_path] = contents if type(contents) == bytes else contents.encode('utf-8')

    def open_file(self, path: str, mode: str) -> IO[Any]:
        normalized_path = os.path.normpath(path)
        if normalized_path in self.open_files:
            raise RuntimeError(f"file '{normalized_path}' is already open")
        if 'r' in mode and normalized_path not in self.files:
            raise FileNotFoundError(normalized_path)
        if 'w' in mode and normalized_path not in self.files:
            for directory_path in self.directories:
                if is_subpath_or_path(normalized_path, directory_path):
                    raise RuntimeError(f"cannot create file '{normalized_path}' -- '{directory_path}' is a directory")
            directory = os.path.dirname(normalized_path)
            if directory and not self.is_directory(directory):
                raise RuntimeError(f"directory '{directory}' doesn't exist")
            self.files[normalized_path] = b''
        
        self.open_files.add(normalized_path)

        def on_close(file: FileMock):
            self.files[normalized_path] = file.getvalue()
            self.open_files.remove(normalized_path)

        return FileMock(self.files[normalized_path], on_close)

    def open_tarfile(self, archive_path: str, mode: str):
        normalized_path = os.path.normpath(archive_path)

        if normalized_path in self.open_files:
            raise RuntimeError(f"file '{normalized_path}' is already open")

        file_exists = normalized_path in self.files

        if mode == 'r:gz':
            if file_exists:
                if not isinstance(self.files[normalized_path], ArchiveMock):
                    raise RuntimeError(f"file '{normalized_path}' is not an archive")
            else:
                raise FileNotFoundError(normalized_path)
        elif mode == 'w:gz':
            if not file_exists:
                for directory_path in self.directories:
                    if is_subpath_or_path(normalized_path, directory_path):
                        raise RuntimeError(
                            f"cannot create file '{normalized_path}' -- '{directory_path}' is a directory")
                directory = os.path.dirname(normalized_path)
                if directory and not self.is_directory(directory):
                    raise RuntimeError(f"directory '{directory}' doesn't exist")
        else:
            raise RuntimeError(f"FileSystemMock doesn't support mode '{mode}'")
    
        self.open_files.add(normalized_path)

        if file_exists:
            archive = self.files[normalized_path]
        else:
            self.files[normalized_path] = archive = ArchiveMock({})
        
        archive.file_system = self
        archive.on_close = lambda archive: self.open_files.remove(normalized_path)

        return archive

    def remove_file(self, path: str) -> None:
        normalized_path = os.path.normpath(path)
        if normalized_path not in self.files:
            raise FileNotFoundError(normalized_path)
        self.files.pop(normalized_path)

    def remove_file_if_it_exists(self, path) -> None:
        if self.exists(path):
            self.remove_file(path)

    def remove_directory_recursively(self, directory: str) -> None:
        normalized_path = os.path.normpath(directory)
        if not self.is_directory(normalized_path):
            raise RuntimeError("'{normalized_path}' is not a directory")

        removed_files = {f for f in self.files if is_subpath_or_path(normalized_path, f)}
        removed_directories = {d for d in self.directories if is_subpath_or_path(normalized_path, d)}
        
        if not removed_files and not removed_directories:
            raise RuntimeError(f"directory {normalized_path} doesn't exist")
        
        for removed_file in removed_files:
            self.files.pop(removed_file)
            tail = os.path.normpath(os.path.dirname(removed_file))
            if tail:
                self.directories.add(tail)

        for removed_directory in removed_directories:
            self.directories.remove(removed_directory)
            tail = os.path.normpath(os.path.dirname(removed_directory))
            if tail:
                self.directories.add(tail)
        self.directories = unique_directories(self.directories)

    def remove_directory_recursively_if_it_exists(self, directory: str) -> None:
        if self.exists(directory):
            self.remove_directory_recursively(directory)

    def print(self, *args, **kwargs):
        if kwargs.pop('clear_current_line', True):
            print('\033[2K', end='', file=self.stdout)
        print(*args, **kwargs, file=self.stdout)

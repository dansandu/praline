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
    def __init__(self, contents: bytes, on_close: Callable[[bytes], None]):
        super(FileMock, self).__init__(contents)
        self.on_close = on_close

    def __exit__(self, type, value, traceback):
        self.on_close(self.getvalue())
        super(FileMock, self).__exit__(type, value, traceback)


class ArchiveMemberMock:
    def __init__(self, name: str, contents: bytes):
        self.name     = name
        self.contents = contents

    def isfile(self) -> bool:
        return True


class ArchiveMock:
    def __init__(self, file_system, contents: bytes, on_close: Callable[[bytes], None]):
        self.file_system = file_system
        self.members     = pickle.loads(contents)
        self.on_close    = on_close

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
        self.file_system.create_directory_if_missing(os.path.dirname(path))
        with self.file_system.open_file(path, 'wb') as f:
            f.write(member.contents)

    def extractfile(self, archive_file_path: str):
        def on_close(contents: bytes):
            self.members[archive_file_path] = contents

        return FileMock(self.members[archive_file_path], on_close)

    def __exit__(self, type, value, traceback):
        self.on_close(pickle.dumps(self.members))


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
                 on_which: Callable[[str], str] = lambda _: None,
                 on_execute: Callable[[List[str], List[str]], bool] = lambda _: None):
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

    def execute_and_fail_on_bad_return(self, command: List[str], add_to_library_path: List[str] = []) -> None:
        if not self.on_execute(command, add_to_library_path):
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

        def on_close(contents: bytes):
            self.files[normalized_path] = contents
            self.open_files.remove(normalized_path)

        return FileMock(self.files[normalized_path], on_close)

    def open_tarfile(self, archive_path: str, mode: str):
        normalized_path = os.path.normpath(archive_path)
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
            self.files[normalized_path] = pickle.dumps({})

        self.open_files.add(normalized_path)

        def on_close(contents: bytes):
            self.files[normalized_path] = contents
            self.open_files.remove(normalized_path)

        return ArchiveMock(self, self.files[normalized_path], on_close)

    def remove_file(self, path: str) -> None:
        normalized_path = os.path.normpath(path)
        if normalized_path not in self.files:
            raise FileNotFoundError(normalized_path)
        self.files.pop(normalized_path)

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

from logging import getLogger
from praline.common.tracing import trace
from subprocess import Popen, PIPE
from os import access, X_OK, makedirs as make_directories, getcwd as current_working_directory, walk, sep as separator, name as os_name, scandir as scan_directory, remove, pathsep, environ as environment, scandir
from os.path import join, exists, isdir as is_directory, isfile as is_file, dirname as directory_name, relpath as relative_path, basename, splitext as split_extension
from shutil import copyfile, copyfileobj, copy, rmtree as remove_directory_recursively
from sys import platform

logger = getLogger(__name__)


def execute(command, add_to_library_path=[]):
    environment_copy = dict(environment)
    if add_to_library_path:
        if platform == 'linux' or platform == 'darwin':
            environment_copy['LD_LIBRARY_PATH'] = pathsep + pathsep.join(add_to_library_path)
        elif platform == 'win32':
            environment_copy['PATH'] += pathsep + pathsep.join(add_to_library_path)
        else:
            raise RuntimeError("Couldn't add to library path -- unsupported platform")
    process = Popen(command, shell=os_name is 'nt', stdout=PIPE, stderr=PIPE, env=environment_copy)
    stdout, stderror = process.communicate()
    return process.returncode, stdout, stderror


@trace
def execute_and_fail_on_bad_return(command, add_to_library_path=[]):
    status, stdout, stderror = execute(command, add_to_library_path=add_to_library_path)
    if stdout:
        logger.info(stdout.decode())
    if stderror:
        logger.error(stderror.decode())
    if status != 0:
        raise RuntimeError(f"command exited with return code {status}")


def files_in_directory(directory):
    for root, file_name in split_files_in_directory(directory):
        yield join(root, file_name)


def top_level_entries_in_directory(directory):
    for entry in scan_directory(directory):
        yield entry


def split_files_in_directory(directory):
    for root, _, files in walk(directory):
        for file_name in files:
            yield root, file_name


def create_directory_if_missing(path):
    if not exists(path):
        logger.debug(f"creating directory {path}")
        make_directories(path)
    elif not is_directory(path):
        raise RuntimeError(f"{path} already exists and is not a directory")


def create_file_if_missing(path, contents=""):
    if not exists(path):
        logger.debug(f"creating file {path}")
        make_directories(name=directory_name(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(contents)
    elif not is_file(path):
        raise RuntimeError(f"{path} already exists and is not a file")


@trace
def copy_files_with_relative_directories(source_root, destination_root, predicate=None):
    for path, _, files in walk(source_root):
        for file_name in files:
            source = join(path, file_name)
            if predicate is None or predicate(source):
                destination = join(destination_root, relative_path(path, source_root))
                make_directories(destination, exist_ok=True)
                copy(source, destination)


@trace
def which(thing):
    directories = environment["PATH"].split(pathsep)
    current = directory_name(thing)
    if current:
        directories.append(current)
    for directory in directories:
        if exists(directory):
            for entry in scan_directory(directory):
                path = join(directory, entry.name)
                if thing == split_extension(entry.name)[0] and access(path, X_OK) and entry.is_file():
                    return entry.path
    return None

def is_directory_empty(directory):
    return len([d for d in scan_directory(directory)]) == 0

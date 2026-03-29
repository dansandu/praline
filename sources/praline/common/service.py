from praline.common import ArtifactPrefix
from praline.common.exception import ServiceConfigurationException
from praline.common.file_system import basename, get_path_without_extension
from typing import List


def artifact_prefix_matches_path(artifact_prefix: ArtifactPrefix, path: str):
    base = basename(path)
    stem = get_path_without_extension(get_path_without_extension(base))
    scope = 'test' if stem == 'test' else 'main'
    return base.startswith(artifact_prefix.prefix) and scope == artifact_prefix.scope


def get_service_executable(executable_prefix: ArtifactPrefix, executables: List[str]):
    if executable_prefix == None:
        raise ServiceConfigurationException("Executable prefix cannot be null")

    candidate_executables = [
        executable for executable in executables
            if artifact_prefix_matches_path(executable_prefix, executable)
    ]

    if len(candidate_executables) == 0:
        return None
    elif len(candidate_executables) > 1:
        raise ServiceConfigurationException(
            f"Multiple executables were found matching the artifact prefix '{executable_prefix}'")

    return candidate_executables[0]


def get_service_library(library_prefix: ArtifactPrefix, libraries: List[str]):
    if library_prefix == None:
        raise ServiceConfigurationException("Library prefix cannot be null")

    candidate_libraries_to_load = [
        library for library in libraries
            if artifact_prefix_matches_path(library_prefix, library)
    ]

    if len(candidate_libraries_to_load) == 0:
        return None
    elif len(candidate_libraries_to_load) > 1:
        raise ServiceConfigurationException(
            f"Multiple libraries were found matching the artifact prefix '{library_prefix}'")

    return candidate_libraries_to_load[0]

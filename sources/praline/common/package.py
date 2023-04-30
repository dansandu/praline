from praline.common import (ArtifactManifest, DependencyScope, DependencyVersion, PackageVersion, package_extension,
                            package_name_pattern)
from praline.common.algorithm.general import cartesian_product
from praline.common.algorithm.graph.instance_traversal import multiple_instance_depth_first_traversal
from praline.common.compiling.compiler import get_compiler_supplier
from praline.common.file_system import FileSystem, basename, common_path, join, normalized_path
from praline.common.tracing import trace

import logging
import pickle
from typing import Dict, List, Tuple


logger = logging.getLogger(__name__)


class InvalidPackageContentsError(Exception):
    pass


class InvalidPackageNameError(Exception):
    pass


class UnsatisfiableArtifactDependenciesError(Exception):
    pass


class UnsatisfiableArtifactDependencyError(Exception):
    pass


class ArtifactCyclicDependenciesError(Exception):
    pass


class InvalidManifestFileError(Exception):
    pass


manifest_file_name = '.manifest'


def write_artifact_manifest(file_system: FileSystem, manifest_path: str, artifact_manifest: ArtifactManifest):
    with file_system.open_file(manifest_path, 'wb') as f:
        pickle.dump(artifact_manifest, f)


def read_artifact_manifest(file_system: FileSystem, package_path: str) -> ArtifactManifest:
    with file_system.open_tarfile(package_path, 'r:gz') as archive:
        with archive.extractfile(manifest_file_name) as f:
            data = pickle.load(f)
            if isinstance(data, ArtifactManifest):
                return data
            else:
                raise InvalidManifestFileError(f"the manifest file is invalid for the package '{package_path}'")


def split_package_version(package_name: str) -> str:
    return package_name[:-len(package_extension)].rsplit('-', 1)


@trace
def get_matching_packages(dependency: str, candidate_packages: List[str]) -> List[str]:
    matching_versions = []
    identifier, version = split_package_version(dependency)
    dependency_version = DependencyVersion.from_string(version)
    for candidate in candidate_packages:
        candidate_identifier, candidate_version = split_package_version(candidate)
        if identifier == candidate_identifier:
            package_version = PackageVersion.from_string(candidate_version)
            if dependency_version.matches(package_version):
                matching_versions.append(package_version)
    sorted_versions = sorted(matching_versions, reverse=True)
    return [f"{identifier}-{version}{package_extension}" for version in sorted_versions]


@trace
def get_packages_from_directory(file_system: FileSystem, directory: str) -> List[str]:
    return [entry.name for entry in file_system.list_directory(directory) 
            if package_name_pattern.fullmatch(entry.name)]


def get_package_dependencies_from_archive(file_system: FileSystem, package_path: str) -> List[str]:
    artifact_manifest = read_artifact_manifest(file_system, package_path)
    return artifact_manifest.get_package_dependencies_file_names()


@trace
def get_package_dependencies_recursively(file_system: FileSystem, 
                                         artifact_manifest: ArtifactManifest,
                                         repository_path: str) -> List[str]:
    root_package      = artifact_manifest.get_package_file_name()
    root_dependencies = artifact_manifest.get_package_dependencies_file_names()

    candidate_packages = get_packages_from_directory(file_system, repository_path)

    def no_version_conflicts(package, dependency_tree):
        package_identifier, package_version = split_package_version(package)
        for dependency in dependency_tree:
            dependency_identifier, dependency_version = split_package_version(dependency)
            if package_identifier == dependency_identifier and package_version != dependency_version:
                return False
        return True

    def no_cyclic_depedencies(cycle: List[str]):
        raise ArtifactCyclicDependenciesError(f"artifact '{root_package}' has cyclic dependencies {cycle}")

    def visitor(package):
        if package == root_package:
            dependencies = root_dependencies
        else:
            dependencies = get_package_dependencies_from_archive(file_system, join(repository_path, package))
        fixed_dependencies = []
        for dependency in dependencies:
            matching_packages = get_matching_packages(dependency, candidate_packages)
            if not matching_packages:
                raise UnsatisfiableArtifactDependencyError(
                    f"couldn't find any package matching '{dependency}' "
                    f"when solving dependencies for package '{package}'")
            fixed_dependencies.append(matching_packages)
        return cartesian_product(fixed_dependencies)

    dependency_trees = multiple_instance_depth_first_traversal(root_package, 
                                                               visitor, 
                                                               no_version_conflicts, 
                                                               no_cyclic_depedencies)
    if not dependency_trees:
        raise UnsatisfiableArtifactDependenciesError(f"dependencies for package '{root_package}' cannot be satisfied")
    dependencies = [dependency for dependency in dependency_trees[0]]
    dependencies.remove(root_package)
    return dependencies


@trace
def pack(file_system: FileSystem, package_path: str, package_files: List[Tuple[str, str]]):
    with file_system.open_tarfile(package_path, 'w:gz') as archive:
        for file_path, package_file_path in package_files:
            archive.add(file_path, package_file_path)


@trace
def unpack(file_system: FileSystem, package_path: str, extraction_path: str) -> Dict[str, List[str]]:
    contents = {
        'resources': [],
        'headers': [],
        'libraries': [],
        'libraries_interfaces': [],
        'symbols_tables': [],
        'executables': []
    }

    with file_system.open_tarfile(package_path, 'r:gz') as archive:
        for member in archive.getmembers():
            if member.isfile():
                valid = False
                for root, files in contents.items():
                    if common_path([normalized_path(member.name), normalized_path(root)]) == normalized_path(root):
                        archive.extract(member, extraction_path)
                        files.append(join(extraction_path, member.name))
                        valid = True
                if member.name != manifest_file_name and not valid:
                    raise InvalidPackageContentsError(f"unrecognized file '{member.name}' in package")
    
    for header in contents['headers']:
        with file_system.open_file(header, 'rb') as f:
            text = f.read().decode()
        with file_system.open_file(header, 'wb') as f:
            f.write(text.replace('PRALINE_EXPORT', 'PRALINE_IMPORT').encode())
    return contents


@trace
def get_package_contents(file_system: FileSystem, package_path: str, extraction_path: str) -> Dict[str, List[str]]:
    contents = {
        'resources': [],
        'headers': [],
        'libraries': [],
        'libraries_interfaces': [],
        'symbols_tables': [],
        'executables': []
    }

    with file_system.open_tarfile(package_path, 'r:gz') as archive:
        for member in archive.getmembers():
            if member.isfile():
                valid = False
                for root, files in contents.items():
                    if common_path([normalized_path(member.name), normalized_path(root)]) == normalized_path(root):
                        files.append(join(extraction_path, member.name))
                        valid = True
                if member.name != manifest_file_name and not valid:
                    raise InvalidPackageContentsError(f"unrecognized file '{member.name}' in package")    
    return contents


@trace
def clean_up_package(file_system: FileSystem, package_path: str, extraction_path: str):
    package_name = basename(package_path)
    match        = package_name_pattern.fullmatch(package_name)
    if not match:
        raise RuntimeError(f"invalid package name '{package_name}'")
    
    organization = match['organization']
    artifact     = match['artifact']
    compiler     = match['compiler']

    resources = join(extraction_path, 'resources', organization, artifact)
    headers   = join(extraction_path, 'headers', organization, artifact)

    file_system.remove_directory_recursively_if_it_exists(resources)
    file_system.remove_directory_recursively_if_it_exists(headers)

    if 'SNAPSHOT' in package_name:
        artifact_identifer = package_name[:-27]
    else:
        artifact_identifer = package_name[:-7]

    compiler_supplier = get_compiler_supplier(compiler)
    yield_descriptor  = compiler_supplier.get_yield_descriptor()
    
    library = yield_descriptor.get_library(join(extraction_path, 'libraries'), artifact_identifer)
    
    library_interface = yield_descriptor.get_library_interface(join(extraction_path, 'libraries_interfaces'), 
                                                               artifact_identifer)
    
    symbols_table = yield_descriptor.get_symbols_table(join(extraction_path, 'symbols_tables'), artifact_identifer) 
    
    executable = yield_descriptor.get_executable(join(extraction_path, 'executables'), artifact_identifer)

    file_system.remove_file_if_it_exists(executable)
    file_system.remove_file_if_it_exists(library)
    file_system.remove_file_if_it_exists(library_interface)
    file_system.remove_file_if_it_exists(symbols_table)
    file_system.remove_file_if_it_exists(package_path)

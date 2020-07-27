from dataclasses import dataclass
from praline.common.algorithm.general import cartesian_product
from praline.common.algorithm.graph.instance_traversal import multiple_instance_depth_first_traversal
from praline.common.compiling.compiler import get_compiler
from praline.common.compiling.yield_descriptor import YieldDescriptor
from praline.common.constants import get_artifact_full_name, package_extension, fixed_package_pattern
from praline.common.file_system import basename, directory_name, FileSystem, join, normalized_path, common_path
from praline.common.hashing import hash_file, key_delta
from praline.common.pralinefile import pralinefile_from_reader
from praline.common.tracing import trace
from typing import Any, Dict, List, Tuple


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


def get_package_metadata(package_path: str, none_on_error: bool = False):
    package_name = basename(package_path)
    match = fixed_package_pattern.fullmatch(package_name)
    if match:
        tokens = match.groupdict()
        return {
            'name':         package_name,
            'organization': tokens['organization'],
            'artifact':     tokens['artifact'],
            'architecture': tokens['architecture'],
            'platform':     tokens['platform'],
            'compiler':     tokens['compiler'],
            'mode':         tokens['mode'],
            'version':      (int(tokens['major']), int(tokens['minor']), int(tokens['bugfix']))
        }
    elif none_on_error:
        return None
    else:
        raise InvalidPackageNameError(package_name)

def split_package(package: str) -> str:
    return package.replace(package_extension, '').rsplit('-', 1)


def get_version(version: str) -> Tuple[int, int, int]:
    major, minor, bugfix = version.split('.')
    return (int(major), int(minor.replace('+', '')), int(bugfix.replace('+', '')))


def get_wildcard(version: str) -> Tuple[bool, bool, bool]:
    _, minor, bugfix = version.split('.')
    return (False, '+' in minor, '+' in bugfix)


def packages_match(fixed_package: str, wildcard_package: str) -> bool:
    fixed_identifier, raw_fixed_version = split_package(fixed_package)
    wildcard_identifier, raw_wildcard_version = split_package(wildcard_package)
    
    if fixed_identifier != wildcard_identifier:
        return False
    
    fixed_version    = get_version(raw_fixed_version)
    wildcard_version = get_version(raw_wildcard_version)
    wildcard         = get_wildcard(raw_wildcard_version)

    for i in range(len(wildcard)):
        if wildcard[i] and wildcard_version[i] <= fixed_version[i] or not wildcard[i] and wildcard_version[i] == fixed_version[i]:
            continue
        else:
            return False
    return True


def get_package(organization: str, artifact: str, architecture: str, platform: str, compiler: str, mode: str, version: str) -> str:
    return f"{get_artifact_full_name(organization, artifact, architecture, platform, compiler, mode, version)}{package_extension}"


@trace
def get_packages_from_directory(file_system: FileSystem, directory: str) -> List[str]:
    return [entry.name for entry in file_system.list_directory(directory) if get_package_metadata(entry.name, none_on_error=True)]


def get_package_dependencies_from_pralinefile(pralinefile: Dict[str, Any], architecture: str, platform: str, compiler: str, mode: str) -> List[str]:
    packages = []
    for dependency in pralinefile['dependencies']:
        package = get_package(dependency['organization'], dependency['artifact'], architecture, platform, compiler, mode, dependency['version'])
        packages.append(package)
    return packages


def get_package_dependencies_from_archive(file_system: FileSystem, package_path: str, scope: str) -> List[str]:
    with file_system.open_tarfile(package_path, 'r:gz') as archive:
        with archive.extractfile('Pralinefile') as reader:
            pralinefile = pralinefile_from_reader(reader, skip_validation=True)
    package = get_package_metadata(package_path)
    package_dependencies = []
    for dependency in pralinefile['dependencies']:
        if dependency['scope'] == scope:
            package_dependency = get_package(dependency['organization'], dependency['artifact'], package['architecture'], package['platform'], package['compiler'], package['mode'], dependency['version'])
            package_dependencies.append(package_dependency)
    return package_dependencies


@trace
def get_matching_packages(package, candidate_packages) -> List[str]:
    def key(package):
        return get_version(split_package(package)[1])

    matching_packages = [candidate for candidate in candidate_packages if packages_match(candidate, package)]
    return sorted(matching_packages, key=key, reverse=True)


@trace
def get_package_dependencies_recursively(file_system: FileSystem,
                                         root_package: str,
                                         root_package_dependencies: List[str],
                                         repository_path: str) -> List[str]:
    candidate_packages = get_packages_from_directory(file_system, repository_path)

    def no_version_conflicts(package, dependency_tree):
        package_identifier, package_version = split_package(package)
        for dependency in dependency_tree:
            dependency_identifier, dependency_version = split_package(dependency)
            if package_identifier == dependency_identifier and package_version != dependency_version:
                return False
        return True

    def no_cyclic_depedencies(cycle: List[str]):
        raise ArtifactCyclicDependenciesError(f"artifact '{root_package}' has cyclic dependencies {cycle}")

    def visitor(package):
        if package == root_package:
            dependencies = root_package_dependencies
        else:
            package_path = join(repository_path, package)
            dependencies = get_package_dependencies_from_archive(file_system, package_path, 'main')
        fixed_dependencies = []
        for dependency in dependencies:
            matching_packages = get_matching_packages(dependency, candidate_packages)
            if not matching_packages:
                raise UnsatisfiableArtifactDependencyError(f"couldn't find any package matching '{dependency}' when solving dependencies for package '{package}'")
            fixed_dependencies.append(matching_packages)
        return cartesian_product(fixed_dependencies)

    dependency_trees = multiple_instance_depth_first_traversal(root_package, visitor, no_version_conflicts, no_cyclic_depedencies)
    if not dependency_trees:
        raise UnsatisfiableArtifactDependenciesError(f"dependencies for package '{root_package}' cannot be satisfied")
    dependencies = [dependency for dependency in dependency_trees[0]]
    dependencies.remove(root_package)
    return dependencies


@trace
def pack(file_system: FileSystem, package_path: str, package_files: List[Tuple[str, str]], cache: Dict[str, Any]):
    hasher = lambda p: hash_file(file_system, p)
    updated, removed, new_cache = key_delta([p for p, _ in package_files], hasher, cache)
    if updated or removed or not file_system.exists(package_path):
        with file_system.open_tarfile(package_path, 'w:gz') as archive:
            for file_path, package_file_path in package_files:
                archive.add(file_path, package_file_path)
    cache.clear()
    cache.update(new_cache)


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
                extracted = False
                for root, files in contents.items():
                    if common_path([normalized_path(member.name), normalized_path(root)]) == root:
                        archive.extract(member, extraction_path)
                        files.append(join(extraction_path, member.name))
                        extracted = True
                if not extracted and member.name != 'Pralinefile':
                    raise InvalidPackageContentsError(f"unrecognized file '{member.name}' in package")
    for header in contents['headers']:
        with file_system.open_file(header, 'rb') as f:
            text = f.read().decode()
        with file_system.open_file(header, 'wb') as f:
            f.write(text.replace('PRALINE_EXPORT', 'PRALINE_IMPORT').encode())
    return contents


@trace
def clean_up_package(file_system: FileSystem, package_path: str, extraction_path: str):
    package           = get_package_metadata(package_path)
    name              = package['name'].replace(package_extension, '')
    organization      = package['organization']
    artifact          = package['artifact']
    architecture      = package['architecture']
    platform          = package['platform']
    compiler          = package['compiler']
    mode              = package['mode']
    yield_descriptor  = get_compiler(file_system, compiler, architecture, platform, mode).get_yield_descriptor()
    resources         = join(extraction_path, 'resources', organization, artifact)
    headers           = join(extraction_path, 'headers', organization, artifact)
    library           = yield_descriptor.get_library(join(extraction_path, 'libraries'), name)
    library_interface = yield_descriptor.get_library_interface(join(extraction_path, 'libraries_interfaces'), name)
    symbols_table     = yield_descriptor.get_symbols_table(join(extraction_path, 'symbols_tables'), name)
    executable        = yield_descriptor.get_executable(join(extraction_path, 'executables'), name)
    
    if file_system.exists(resources):
        file_system.remove_directory_recursively(resources)
    
    if file_system.exists(headers):
        file_system.remove_directory_recursively(headers)
    
    if library and file_system.exists(library):
        file_system.remove_file(library)
    
    if library_interface and file_system.exists(library_interface):
        file_system.remove_file(library_interface)
    
    if symbols_table and file_system.exists(symbols_table):
        file_system.remove_file(symbols_table)

    if executable and file_system.exists(executable):
        file_system.remove_file(executable)

    if file_system.exists(package_path):
        file_system.remove_file(package_path)


@trace
def get_package_extracted_contents(file_system: FileSystem, package_path: str, extraction_path: str) -> Dict[str, List[str]]:
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
                extracted = False
                for root, files in contents.items():
                    if common_path([normalized_path(member.name), normalized_path(root)]) == root:
                        files.append(join(extraction_path, member.name))
                        extracted = True
                if not extracted and member.name != 'Pralinefile':
                    raise InvalidPackageContentsError(f"unrecognized file '{member.name}' in package")    
    return contents

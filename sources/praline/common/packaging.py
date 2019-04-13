from re import compile as compile_regex
from tarfile import open as open_tarfile

from praline.common.file_system import basename, create_directory_if_missing, directory_name, exists, join, remove, remove_directory_recursively
from praline.common.hashing import hash_file, key_delta
from praline.common.pralinefile import pralinefile_from_reader
from praline.common.pralinefile.constants import version_regex
from praline.common.tracing import trace

package_pattern = compile_regex(fr'(?P<organization>[a-z]+)-(?P<artifact>[a-z]+(_[a-z]+)*)-(?P<architecture>x86|x86_64|arm)-(?P<platform>linux|windows|darwin)-(?P<compiler>gcc|clang)-{version_regex}\.tar\.gz')

package_extension = '.tar.gz'

executable_extension = '.exe'

library_extension = '.so'


def package_metadata(package, none_on_failure=False):
    match = package_pattern.fullmatch(package)
    if match:
        tokens = match.groupdict()
        return {
            'organization': tokens['organization'],
            'artifact': tokens['artifact'],
            'architecture': tokens['architecture'],
            'platform': tokens['platform'],
            'compiler': tokens['compiler'],
            'version': (int(tokens['major']), int(tokens['minor']), int(tokens['bugfix'])),
            'wildcard': (False, bool(tokens['minor_wildcard']), bool(tokens['bugfix_wildcard'])),
            'identifier': package.rsplit('-', 1)[0],
            'package': package
        }
    if none_on_failure:
        return None
    raise RuntimeError(f"invalid package name {package}")


def package_from_pralinefile(pralinefile, architecture, platform, compiler):
    return f"{pralinefile['organization']}-{pralinefile['artifact']}-{architecture}-{platform}-{compiler}-{pralinefile['version']}{package_extension}"


def dependant_packages_from_pralinefile(pralinefile, architecture, platform, compiler):
    packages = []
    for dependency in pralinefile['dependencies']:
        packages.append(f"{dependency['organization']}-{dependency['artifact']}-{architecture}-{platform}-{compiler}-{dependency['version']}{package_extension}")
    return packages


def dependant_packages_from_package(package_path, scope):
    metadata = package_metadata(basename(package_path))
    with open_tarfile(package_path) as tarfile:
        with tarfile.extractfile('Pralinefile') as reader:
            pralinefile = pralinefile_from_reader(reader, skip_validation=True)
    packages = []
    for dependency in pralinefile['dependencies']:
        if dependency['scope'] == scope:
            packages.append(f"{dependency['organization']}-{dependency['artifact']}-{metadata['architecture']}-{metadata['platform']}-{metadata['compiler']}-{dependency['version']}{package_extension}")
    return packages


@trace
def create_package(directory, pralinefile, architecture, platform, compiler, files_to_package, cache):
    create_directory_if_missing(directory)
    package = package_from_pralinefile(pralinefile, architecture, platform, compiler)
    package_path = join(directory, package)
    updated, removed, new_cache = key_delta([path for path, _ in files_to_package], cache, key_hasher=hash_file)
    if updated or removed or not exists(package_path):
        with open_tarfile(package_path, 'w:gz') as archive:
            for path, name in files_to_package:
                archive.add(path, name)
    cache.clear()
    cache.update(new_cache)
    return package_path


@trace
def extract_package(package_path, extraction_point):
    executables_destination = join(extraction_point, 'executables')
    libraries_destination = join(extraction_point, 'libraries')
    
    package = basename(package_path)
    executable = package.replace(package_extension, executable_extension)
    library = package.replace(package_extension, library_extension)

    metadata = package_metadata(package)
    organization = metadata['organization']
    artifact = metadata['artifact']
    header_prefix = f'headers/{organization}/{artifact}/'
    resource_prefix = f'resources/{organization}/{artifact}/'

    libraries = []
    with open_tarfile(package_path, 'r:gz') as archive:
        for member in archive.getmembers():
            if member.isfile():
                if member.name.startswith(header_prefix) and member.name.endswith('.hpp') or member.name.startswith(resource_prefix):
                    archive.extract(member, extraction_point)
                elif member.name == executable:
                    archive.extract(member, executables_destination)
                elif member.name == library:
                    archive.extract(member, libraries_destination)
                    libraries.append(member.name)
    return libraries


@trace
def libraries_from_package(package_path):
    with open_tarfile(package_path, 'r:gz') as archive:
        return [m.name for m in archive.getmembers() if m.isfile() and not directory_name(m.name) and m.name.endswith(library_extension)]


@trace
def clean_up_package(package_path, extraction_point):
    package = basename(package_path)
    executable = join(extraction_point, 'executables', package.replace(package_extension, executable_extension))
    library = join(extraction_point, 'libraries', package.replace(package_extension, library_extension))

    metadata = package_metadata(package)
    organization = metadata['organization']
    artifact = metadata['artifact']
    resources = join(extraction_point, 'resources', organization, artifact)
    headers = join(extraction_point, 'headers', organization, artifact)

    if exists(resources):
        remove_directory_recursively(resources)
    if exists(headers):
        remove_directory_recursively(headers)
    if exists(executable):
        remove(executable)
    if exists(library):
        remove(library)
    if exists(package_path):
        remove(package_path)

from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join
from praline.common.hashing import key_delta
from praline.common.package import clean_up_package, get_package_extracted_contents, unpack
from typing import Any, Dict


@stage(requirements=[['project_directory', 'pralinefile', 'compiler']],
       output=['external_resources_root', 'external_headers_root', 'external_executables_root', 'external_libraries_root', 'external_libraries_interfaces_root', 'external_symbols_tables_root',
               'external_resources', 'external_headers', 'external_executables', 'external_libraries', 'external_libraries_interfaces', 'external_symbols_tables'],
       cacheable=True, exposed=True)
def pull_dependencies(file_system: FileSystem, 
                      resources: StageResources, 
                      cache: Dict[str, Any], 
                      program_arguments: Dict[str, Any], 
                      configuration: Dict[str, Any], 
                      remote_proxy: RemoteProxy,
                      progressBarSupplier: ProgressBarSupplier):
    project_directory      = resources['project_directory']
    external_root          = join(project_directory, 'target', 'external')
    external_packages_root = join(external_root, 'packages')

    resources['external_resources_root']            = external_resources_root            = join(external_root, 'resources')
    resources['external_headers_root']              = external_headers_root              = join(external_root, 'headers')
    resources['external_executables_root']          = external_executables_root          = join(external_root, 'executables')
    resources['external_libraries_root']            = external_libraries_root            = join(external_root, 'libraries')
    resources['external_libraries_interfaces_root'] = external_libraries_interfaces_root = join(external_root, 'libraries_interfaces')
    resources['external_symbols_tables_root']       = external_symbols_tables_root       = join(external_root, 'symbols_tables')

    file_system.create_directory_if_missing(external_packages_root)
    file_system.create_directory_if_missing(external_resources_root)
    file_system.create_directory_if_missing(external_headers_root)
    file_system.create_directory_if_missing(external_executables_root)
    file_system.create_directory_if_missing(external_libraries_root)
    file_system.create_directory_if_missing(external_libraries_interfaces_root)
    file_system.create_directory_if_missing(external_symbols_tables_root)

    external_resources            = []
    external_headers              = []
    external_libraries            = []
    external_libraries_interfaces = []
    external_symbols_tables       = []
    external_executables          = []

    def extend_externals(contents):
        external_resources.extend(contents['resources'])
        external_headers.extend(contents['headers'])
        external_libraries.extend(contents['libraries'])
        external_libraries_interfaces.extend(contents['libraries_interfaces'])
        external_symbols_tables.extend(contents['symbols_tables'])
        external_executables.extend(contents['executables'])

    pralinefile   = resources['pralinefile']
    compiler      = resources['compiler']
    logging_level = program_arguments['global']['logging_level']
    
    packages = remote_proxy.solve_dependencies(pralinefile,
                                               compiler.get_architecture(),
                                               compiler.get_platform(),
                                               compiler.get_name(),
                                               compiler.get_mode())
    updated, removed, new_cache = key_delta(packages.keys(), lambda p: packages[p], cache)
    
    for package in removed:
        package_path = join(external_packages_root, package)
        clean_up_package(file_system, package_path, external_root, logging_level)

    for package in updated:
        package_path = join(external_packages_root, package)
        clean_up_package(file_system, package_path, external_root, logging_level)
        remote_proxy.pull_package(package_path)
        contents = unpack(file_system, package_path, external_root)
        extend_externals(contents)

    for package in packages:
        if package not in updated:
            package_path = join(external_packages_root, package)
            if not file_system.exists(package_path):
                remote_proxy.pull_package(package_path)
                contents = unpack(file_system, package_path, external_root)
            else:
                contents = get_package_extracted_contents(file_system, package_path, external_root)
            extend_externals(contents)

    resources['external_resources']            = external_resources
    resources['external_headers']              = external_headers
    resources['external_libraries']            = external_libraries
    resources['external_libraries_interfaces'] = external_libraries_interfaces
    resources['external_symbols_tables']       = external_symbols_tables
    resources['external_executables']          = external_executables

    cache.clear()
    cache.update(new_cache)

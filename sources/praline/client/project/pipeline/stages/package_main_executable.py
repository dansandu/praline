from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.common.package import get_package, pack, package_extension
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import basename, FileSystem, join, relative_path
from typing import Any, Dict


@stage(requirements=[['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root', 'formatted_headers', 'main_executable', 'main_executable_symbols_table', 'test_results'],
                     ['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root', 'formatted_headers', 'main_executable', 'main_executable_symbols_table'],
                     ['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root',           'headers', 'main_executable', 'main_executable_symbols_table', 'test_results'],
                     ['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root',           'headers', 'main_executable', 'main_executable_symbols_table']],
       output=['main_executable_package'], cacheable=True)
def package_main_executable(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    project_directory = resources['project_directory']
    pralinefile       = resources['pralinefile']
    compiler          = resources['compiler']
    resources_root    = resources['resources_root']
    resource_files    = resources['resources']
    headers_root      = resources['headers_root']
    main_executable               = resources['main_executable']
    main_executable_symbols_table = resources['main_executable_symbols_table']
    if resources.activation in [0, 1]:
        headers = resources['formatted_headers']
    elif resources.activation in [2, 4]:
        headers = resources['headers']

    package_path = join(project_directory, 'target', get_package(pralinefile['organization'],
                                                                 pralinefile['artifact'],
                                                                 compiler.get_architecture(),
                                                                 compiler.get_platform(),
                                                                 compiler.get_name(),
                                                                 compiler.get_mode(),
                                                                 pralinefile['version']))

    package_files = [(path, join('resources', relative_path(path, resources_root))) for path in resource_files]
    package_files.extend((path, join('headers', relative_path(path, headers_root))) for path in headers)
    package_files.append((join(project_directory, 'Pralinefile'), 'Pralinefile'))
    package_files.append((main_executable, f'executables/{basename(main_executable)}'))
    if main_executable_symbols_table:
        package_files.append((main_executable_symbols_table, f'symbols_tables/{basename(main_executable_symbols_table)}'))
    pack(file_system, package_path, package_files, cache)

    resources['main_executable_package'] = package_path

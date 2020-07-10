from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.common.package import get_package, pack, package_extension
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem, join, relative_path
from typing import Any, Dict


def has_headers_only(file_system: FileSystem, program_arguments: Dict[str, Any], configuration: Dict[str, Any]):
    sources_root = join(file_system.get_working_directory(), 'sources')
    files        = file_system.files_in_directory(sources_root)
    return not program_arguments['global']['executable'] and all(f.endswith('.hpp') or f.endswith('.test.cpp') for f in files)


@stage(requirements=[['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root', 'formatted_headers', 'test_results'],
                     ['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root', 'formatted_headers'],
                     ['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root',           'headers', 'test_results'],
                     ['project_directory', 'pralinefile', 'compiler', 'resources_root', 'resources', 'headers_root',           'headers']],
       output=['headers_only_package'], predicate=has_headers_only, cacheable=True)
def package_headers_only(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    project_directory = resources['project_directory']
    pralinefile       = resources['pralinefile']
    compiler          = resources['compiler']
    resources_root    = resources['resources_root']
    resource_files    = resources['resources']
    headers_root      = resources['headers_root']
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
    pack(file_system, package_path, package_files, cache)

    resources['headers_only_package'] = package_path

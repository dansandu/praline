from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.common.package import manifest_file_name, pack, write_artifact_manifest
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join, relative_path

from typing import Any, Dict


@stage(requirements=[['project_structure', 'resources', 'formatted_headers', 'main_executable', 'main_executable_symbols_table', 'test_results'],
                     ['project_structure', 'resources', 'formatted_headers', 'main_executable', 'main_executable_symbols_table'],
                     ['project_structure', 'resources',           'headers', 'main_executable', 'main_executable_symbols_table', 'test_results'],
                     ['project_structure', 'resources',           'headers', 'main_executable', 'main_executable_symbols_table'],
                     ['project_structure', 'resources', 'formatted_headers', 'main_library', 'main_library_interface', 'main_library_symbols_table', 'test_results'],
                     ['project_structure', 'resources', 'formatted_headers', 'main_library', 'main_library_interface', 'main_library_symbols_table'],
                     ['project_structure', 'resources',           'headers', 'main_library', 'main_library_interface', 'main_library_symbols_table', 'test_results'],
                     ['project_structure', 'resources',           'headers', 'main_library', 'main_library_interface', 'main_library_symbols_table'],
                     ['project_structure', 'resources', 'formatted_headers', 'test_results'],
                     ['project_structure', 'resources', 'formatted_headers'],
                     ['project_structure', 'resources',           'headers', 'test_results'],
                     ['project_structure', 'resources',           'headers']],
       output=['package'], exposed=True)
def package(file_system: FileSystem, 
            resources: StageResources, 
            cache: Dict[str, Any], 
            program_arguments: Dict[str, Any], 
            configuration: Dict[str, Any], 
            remote_proxy: RemoteProxy,
            progressBarSupplier: ProgressBarSupplier):
    artifact_manifest  = configuration['artifact_manifest']
    project_structure  = resources['project_structure']
    resource_files     = resources['resources']
    resources_root     = project_structure.resources_root
    headers_root       = project_structure.sources_root
    target_root        = join(project_structure.project_directory, 'target')
    manifest_file_path = join(target_root, manifest_file_name)

    write_artifact_manifest(file_system, manifest_file_path, artifact_manifest)

    if 'formatted_headers' in resources:
        headers = resources['formatted_headers']
    else:
        headers = resources['headers']

    package_files = [(path, join('resources', relative_path(path, resources_root))) for path in resource_files]

    package_files.extend((path, join('headers', relative_path(path, headers_root))) for path in headers)

    package_files.append((manifest_file_path, manifest_file_name))

    if resources.activation in [0, 1, 2, 3]:
        main_executable               = resources['main_executable']
        main_executable_symbols_table = resources['main_executable_symbols_table']

        package_files.append((main_executable, relative_path(main_executable, target_root)))

        if main_executable_symbols_table:
            package_files.append((main_executable_symbols_table, 
                                  relative_path(main_executable_symbols_table, target_root)))
    elif resources.activation in [4, 5, 6, 7]:
        main_library               = resources['main_library']
        main_library_interface     = resources['main_library_interface']
        main_library_symbols_table = resources['main_library_symbols_table']

        package_files.append((main_library, relative_path(main_library, target_root)))

        if main_library_interface:
            package_files.append((main_library_interface, relative_path(main_library_interface, target_root)))
        if main_library_symbols_table:
            package_files.append((main_library_symbols_table,
                                  relative_path(main_library_symbols_table, target_root)))
    
    package_path = join(project_structure.external_packages_root, 
                        artifact_manifest.get_package_file_name_and_instantiate_snapshot())
    pack(file_system, package_path, package_files)

    resources['package'] = package_path

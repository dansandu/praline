from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.compiling.compiler import link_executable_using_cache
from praline.common.file_system import FileSystem, join, normalized_path
from typing import Any, Dict


@stage(requirements=[['project_directory', 'pralinefile', 'compiler', 'main_executable_object', 'main_objects', 'test_objects', 'external_libraries_root', 'external_libraries_interfaces_root', 'external_libraries', 'external_libraries_interfaces']],
       output=['test_executable', 'test_executable_symbols_table'], cacheable=True)
def link_test_executable(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    project_directory                  = resources['project_directory']
    pralinefile                        = resources['pralinefile']
    organization                       = pralinefile['organization']
    artifact                           = pralinefile['artifact']
    version                            = pralinefile['version']
    compiler                           = resources['compiler']
    objects                            = resources['main_objects'] + resources['test_objects']
    main_executable_object             = resources['main_executable_object']
    external_libraries_root            = resources['external_libraries_root']
    external_libraries_interfaces_root = resources['external_libraries_interfaces_root']
    external_libraries                 = resources['external_libraries']
    external_libraries_interfaces      = resources['external_libraries_interfaces']
    executables_root                   = join(project_directory, 'target', 'executables')
    symbols_tables_root                = join(project_directory, 'target', 'symbols_tables')

    objects = [normalized_path(o) for o in objects]
    if main_executable_object and normalized_path(main_executable_object) in objects:
        objects.remove(normalized_path(main_executable_object))

    (resources['test_executable'],
     resources['test_executable_symbols_table']) = link_executable_using_cache(file_system,
                                                                               compiler,
                                                                               executables_root,
                                                                               symbols_tables_root,
                                                                               external_libraries_root,
                                                                               external_libraries_interfaces_root,
                                                                               objects,
                                                                               external_libraries,
                                                                               external_libraries_interfaces,
                                                                               organization,
                                                                               artifact,
                                                                               version,
                                                                               cache, True)

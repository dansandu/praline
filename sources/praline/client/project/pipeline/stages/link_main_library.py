from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.compiling.compiler import link_library_using_cache
from praline.common.file_system import basename, FileSystem, join
from typing import Any, Dict


def has_non_executable_sources(file_system: FileSystem, program_arguments: Dict[str, Any], configuration: Dict[str, Any]):
    sources_root = join(file_system.get_working_directory(), 'sources')
    files        = file_system.files_in_directory(sources_root)
    return (not program_arguments['global']['executable'] and all(basename(f) != 'executable.cpp' for f in files) and
            any(f.endswith('.cpp') and not f.endswith('.test.cpp') for f in files))


@stage(requirements=[['project_directory', 'pralinefile', 'compiler', 'main_objects', 'external_libraries_root', 'external_libraries_interfaces_root', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_library', 'main_library_interface', 'main_library_symbols_table'],
       predicate=has_non_executable_sources, cacheable=True)
def link_main_library(file_system: FileSystem, 
                      resources: StageResources, 
                      cache: Dict[str, Any], 
                      program_arguments: Dict[str, Any], 
                      configuration: Dict[str, Any], 
                      remote_proxy: RemoteProxy,
                      progressBarSupplier: ProgressBarSupplier):
    project_directory                  = resources['project_directory']
    pralinefile                        = resources['pralinefile']
    organization                       = pralinefile['organization']
    artifact                           = pralinefile['artifact']
    version                            = pralinefile['version']
    compiler                           = resources['compiler']
    main_objects                       = resources['main_objects']
    external_libraries_root            = resources['external_libraries_root']
    external_libraries_interfaces_root = resources['external_libraries_interfaces_root']
    external_libraries                 = resources['external_libraries']
    external_libraries_interfaces      = resources['external_libraries_interfaces']
    libraries_root                     = join(project_directory, 'target', 'libraries')
    libraries_interfaces_root          = join(project_directory, 'target', 'libraries_interfaces')
    symbols_tables_root                = join(project_directory, 'target', 'symbols_tables')

    (resources['main_library'], 
     resources['main_library_interface'],
     resources['main_library_symbols_table']) = link_library_using_cache(file_system,
                                                                         compiler,
                                                                         libraries_root,
                                                                         libraries_interfaces_root,
                                                                         symbols_tables_root,
                                                                         external_libraries_root,
                                                                         external_libraries_interfaces_root,
                                                                         main_objects,
                                                                         external_libraries,
                                                                         external_libraries_interfaces,
                                                                         organization,
                                                                         artifact,
                                                                         version,
                                                                         cache)

from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


main_executable_contents = """\
#include <iostream>

int main(int, char**)
{
    std::cout << "Hello, world!" << std::endl;
    return 0;
}
"""


@stage(requirements=[['pralinefile', 'main_sources_root']], output=['main_sources', 'main_executable_source'])
def load_main_sources(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    main_sources_root      = resources['main_sources_root']
    pralinefile            = resources['pralinefile']
    main_executable_source = join(main_sources_root, pralinefile['organization'], pralinefile['artifact'], 'executable.cpp')
    if program_arguments['global']['executable']:
        resources['main_executable_source'] = main_executable_source
        file_system.create_file_if_missing(main_executable_source, main_executable_contents)
    elif file_system.is_file(main_executable_source):
        resources['main_executable_source'] = main_executable_source
    else:
        resources['main_executable_source'] = None
    resources['main_sources'] = [f for f in file_system.files_in_directory(main_sources_root) if f.endswith('.cpp') and not f.endswith('.test.cpp')]

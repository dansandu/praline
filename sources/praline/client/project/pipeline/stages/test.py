from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem
from typing import Any, Dict


program_arguments = [
    {
        'name': '--arguments',
        'action': 'store',
        'nargs': REMAINDER,
        'dest': 'arguments',
        'help': 'Forward arguments to the underlying executable being run. Be warned that all proceeding arguments are forwarded and no longer used by praline!',
        'default': []
    }
]


@stage(requirements=[['external_libraries_root', 'test_executable']], output=['test_results'],
       exposed=True, program_arguments=program_arguments)
def test(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    external_libraries_root = resources['external_libraries_root']
    test_executable         = resources['test_executable']
    arguments               = program_arguments['byStage']['arguments']

    file_system.execute_and_fail_on_bad_return([test_executable] + arguments,
                                               add_to_library_path=[external_libraries_root],
                                               interactive=True)
    
    resources['test_results'] = 'success'

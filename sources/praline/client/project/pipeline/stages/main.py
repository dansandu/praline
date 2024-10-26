from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import DirectUserMessageException
from praline.common.file_system import ProcessExecutionError


class MainProcessExecutionException(ProcessExecutionError, DirectUserMessageException):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        super().__init__(status, stdout, stderror)


program_arguments = [
    {
        'name': '--arguments',
        'action': 'store',
        'nargs': REMAINDER,
        'dest': 'arguments',
        'help': "Forward arguments to the underlying executable being run. All proceeding arguments are forwarded "
            "and no longer used by praline!",
        'default': []
    }
]


@stage(requirements=[['project_directories', 'main_executable', 'tests_passed'], 
                     ['project_directories', 'main_executable']],
       exposed=True, 
       program_arguments=program_arguments)
def main(arguments: StageArguments):
    file_system       = arguments.file_system 
    resources         = arguments.resources
    project_structure = arguments.project_structure
    program_arguments = arguments.program_arguments['byStage']['arguments']

    main_executable         = resources['main_executable']
    external_libraries_root = project_structure.external_libraries_root
    
    try:
        file_system.execute_and_fail_on_bad_return([main_executable] + program_arguments,
                                                   add_to_library_path=[external_libraries_root],
                                                   interactive=True)
    except ProcessExecutionError as exception:
        raise MainProcessExecutionException(exception.status, exception.stdout, exception.stderror)

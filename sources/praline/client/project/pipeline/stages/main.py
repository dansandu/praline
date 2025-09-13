from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.exception import (
    DirectUserMessageException, MainProcessExecutionException, ProcessExecutionException
)


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


@stage(
    requirements=['project_directories', 'main_executable', 'tests_passed'],
    exposed=True, 
    program_arguments=program_arguments
)
def main(arguments: StageArguments):
    file_system       = arguments.file_system 
    resources         = arguments.resources
    project_structure = arguments.project_structure
    program_arguments = arguments.program_arguments['byStage']['arguments']

    main_executable = resources['main_executable']

    if arguments.skipOrExceptionIf(main_executable == None, "Artifact is not executable"):
        return

    try:
        file_system.execute_and_fail_on_bad_return(
            [main_executable] + program_arguments,
            add_to_library_path=[project_structure.external_libraries_root],
            interactive=True
        )
    except ProcessExecutionException as exception:
        raise MainProcessExecutionException(exception.status, exception.stdout, exception.stderror)

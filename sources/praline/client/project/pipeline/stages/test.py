from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.exception import TestProcessExecutionException, ProcessExecutionException


program_arguments = [
    {
        'name': '--arguments',
        'action': 'store',
        'nargs': REMAINDER,
        'dest': 'arguments',
        'help': "Forward arguments to the underlying executable being run. Be warned that all proceeding arguments "
            "are forwarded and are no longer used by praline!",
        'default': []
    }
]


@stage(
    requirements=['project_directories', 'test_service'],
    output=['tests_passed'],
    exposed=True, 
    program_arguments=program_arguments
)
def test(arguments: StageArguments):
    file_system           = arguments.file_system
    resources             = arguments.resources
    project_structure     = arguments.project_structure
    progress_bar_supplier = arguments.progress_bar_supplier
    program_arguments     = arguments.program_arguments

    service = resources['test_service']

    if any([
        arguments.skipOrExceptionIf(
            arguments.program_arguments['global']['skip_unit_tests'], 
            "Cannot run tests because the skip-unit-tests flag was used"),
        
        arguments.skipOrExceptionIf(
            service.executable_to_run == None, 
            "Cannot run tests because the test service executable is not set"),

        arguments.skipOrExceptionIf(
            service.library_to_load == None, 
            "Cannot run tests because the test service library is not set"),

        arguments.skipOrExceptionIf(
            service.service_name == None, 
            "Cannot run tests because the test service name is not set"),
    ]):
        resources['tests_passed'] = False
        return

    try:
        file_system.execute_and_fail_on_bad_return(
            [service.executable_to_run, service.library_to_load, service.service_name] + program_arguments['byStage']['arguments'],
            add_to_library_path=[project_structure.external_libraries_root],
            interactive=True
        )
    except ProcessExecutionException as exception:
        raise TestProcessExecutionException(exception.status, exception.stdout, exception.stderror)

    resources['tests_passed'] = True

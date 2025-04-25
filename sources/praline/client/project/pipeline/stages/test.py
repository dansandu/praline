from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import DirectUserMessageException
from praline.common.file_system import ProcessExecutionError, basename


class TestProcessExecutionException(ProcessExecutionError, DirectUserMessageException):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        super().__init__(status, stdout, stderror)


class TestServiceRunnerNotSetException(DirectUserMessageException):
    pass


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


@stage(requirements=[['project_directories', 'test_library', 'external_executables', 'main_executable'],
                     ['project_directories', 'test_library', 'external_executables']], 
       output=['tests_passed'],
       exposed=True, 
       program_arguments=program_arguments,
       has_progress_bar=True)
def test(arguments: StageArguments):
    artifact_manifest     = arguments.artifact_manifest
    file_system           = arguments.file_system
    resources             = arguments.resources
    project_structure     = arguments.project_structure
    progress_bar_supplier = arguments.progress_bar_supplier
    program_arguments     = arguments.program_arguments

    test_library         = resources['test_library']
    external_executables = resources['external_executables']
    
    external_libraries_root = project_structure.external_libraries_root

    test_service_runner_executable = None

    if artifact_manifest.test_service_runner != None:
        root_prefix = artifact_manifest.organization + '-' + artifact_manifest.artifact
        if artifact_manifest.test_service_runner == root_prefix and 'main_executable' in resources:
            test_service_runner_executable = resources['main_executable']
        else:
            test_service_runner_executable = next(exe for exe in external_executables if basename(exe).startswith(artifact_manifest.test_service_runner))
    
    if test_service_runner_executable == None:
        raise TestServiceRunnerNotSetException(f"The test service runner is not set -- set it inside the Pralinefile using the test_service_runner field")

    try:
        file_system.execute_and_fail_on_bad_return(
            [test_service_runner_executable, test_library, artifact_manifest.test_service_name] + program_arguments['byStage']['arguments'],
            add_to_library_path=[external_libraries_root],
            interactive=True,
            add_to_env={
                'PRALINE_PROGRESS_BAR_STAGE_INDEX': str(progress_bar_supplier.stage_index),
                'PRALINE_PROGRESS_BAR_STAGE_COUNT': str(progress_bar_supplier.stage_count),
            })
    except ProcessExecutionError as exception:
        raise TestProcessExecutionException(exception.status, exception.stdout, exception.stderror)

    resources['tests_passed'] = 'success'

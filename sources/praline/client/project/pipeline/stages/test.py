from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import DirectUserMessageException
from praline.common.file_system import ProcessExecutionError
from praline.common.service import get_service_executable, get_service_library


class TestProcessExecutionException(ProcessExecutionError, DirectUserMessageException):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        super().__init__(status, stdout, stderror)


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


@stage(requirements=[
            ['project_directories', 'external_executables', 'external_libraries', 'test_library', 'test_executable', 'main_executable', 'main_library'],
            ['project_directories', 'external_executables', 'external_libraries', 'test_library', 'test_executable', 'main_executable'],
            ['project_directories', 'external_executables', 'external_libraries', 'test_library', 'test_executable', 'main_library'],
            ['project_directories', 'external_executables', 'external_libraries', 'test_library', 'main_executable', 'main_library'],
            ['project_directories', 'external_executables', 'external_libraries', 'test_library', 'test_executable'],
            ['project_directories', 'external_executables', 'external_libraries', 'test_library', 'main_executable'],
            ['project_directories', 'external_executables', 'external_libraries', 'test_library', 'main_library'],
            ['project_directories', 'external_executables', 'external_libraries', 'test_library'],
        ],
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

    executables = resources['external_executables'][:]
    
    if 'main_executable' in resources:
        executables.append(resources['main_executable'])
    if 'test_executable' in resources:
        executables.append(resources['test_executable'])

    libraries = resources['external_libraries'][:]
    libraries.append(resources['test_library'])

    if 'main_library' in resources:
        libraries.append(resources['main_library'])

    if artifact_manifest.test_service.library_to_load != None:
        test_library = get_service_library(artifact_manifest.test_service.library_to_load, libraries)
    else:
        test_library = resources['test_library']
    
    test_service_executable = get_service_executable(artifact_manifest.test_service.executable_to_run, executables)

    try:
        file_system.execute_and_fail_on_bad_return(
            [test_service_executable, test_library, artifact_manifest.test_service.service_name] + program_arguments['byStage']['arguments'],
            add_to_library_path=[project_structure.external_libraries_root],
            interactive=True,
            add_to_env={
                'PRALINE_PROGRESS_BAR_STAGE_INDEX': str(progress_bar_supplier.stage_index),
                'PRALINE_PROGRESS_BAR_STAGE_COUNT': str(progress_bar_supplier.stage_count),
            })
    except ProcessExecutionError as exception:
        raise TestProcessExecutionException(exception.status, exception.stdout, exception.stderror)

    resources['tests_passed'] = 'success'

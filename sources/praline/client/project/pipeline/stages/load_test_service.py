from praline.common import ServiceConfiguration
from praline.common.service import get_service_executable, get_service_library
from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_executables', 'external_libraries',
        'main_executable', 'test_executable', 'test_library',
    ], 
    output=['test_service']
)
def load_test_service(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler = arguments.compiler
    resources = arguments.resources

    external_executables = resources['external_executables']
    external_libraries   = resources['external_libraries']
    main_executable      = resources['main_executable']
    test_executable      = resources['test_executable']
    test_library         = resources['test_library']

    executables = []
    executables.extend(external_executables)

    libraries = []
    libraries.extend(external_libraries)

    if main_executable != None:
        executables.extend(main_executable)

    if test_executable != None:
        executables.extend(test_executable)

    if test_library != None:
        libraries.extend(test_library)

    yieldDescriptor = compiler.compiler_strategy.get_yield_descriptor()

    if artifact_manifest.test_service.executable_to_run != None:
        executable_prefix = yieldDescriptor.get_executable_prefix(
            artifact_manifest.test_service.executable_to_run)

        executable = get_service_executable(executable_prefix, executables)
    else:
        executable = test_executable

    if artifact_manifest.test_service.library_to_load != None:
        library_prefix = yieldDescriptor.get_library_prefix(
            artifact_manifest.test_service.library_to_load)

        library = get_service_library(library_prefix, libraries)
    else:
        library = test_library

    resources['test_service'] = ServiceConfiguration(
        executable_to_run=executable,
        library_to_load=library,
        service_name=artifact_manifest.test_service.service_name
    )

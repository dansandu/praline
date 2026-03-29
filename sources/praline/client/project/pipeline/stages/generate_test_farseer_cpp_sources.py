from praline.common import ArtifactPrefix, generated_header_file_extension, generated_source_file_extension
from praline.common.file_system import join, relative_path, get_path_without_extension, directory_name
from praline.common.service import get_service_executable, get_service_library
from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_executables', 'external_libraries', 'main_library',
        'test_farseer_sources',
    ],
    output=['test_farseer_cpp_headers', 'test_farseer_cpp_sources']
)
def generate_test_farseer_cpp_sources(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    resources         = arguments.resources

    farseer_sources = resources['test_farseer_sources']
    executables     = resources['external_executables']
    main_library    = resources['main_library']

    libraries = []
    libraries.extend(resources['external_libraries'])
    if  main_library != None:
        libraries.append(main_library)

    resources['test_farseer_cpp_headers'] = farseer_cpp_headers = []
    resources['test_farseer_cpp_sources'] = farseer_cpp_sources = []

    if arguments.skipOrExceptionIf(
        len(farseer_sources) == 0,
        "There are no test farseer source files the compile"
    ):
        return

    if artifact_manifest.main_service.executable_to_run == None:
        raise RuntimeError("Main service must be configured in order to generate farseer sources")

    yieldDescriptor = compiler.compiler_strategy.get_yield_descriptor()

    executable_prefix = yieldDescriptor.get_executable_prefix(
        artifact_manifest.main_service.executable_to_run)

    library_prefix = yieldDescriptor.get_library_prefix(ArtifactPrefix('dansandu-farseer'))

    service_executable = get_service_executable(executable_prefix, executables)
    service_library = get_service_library(library_prefix, libraries)
    service_name = 'dansandu-farseer-generate_protocol'

    for farseer_source in farseer_sources:
        farseer_cpp_base = join(
            project_structure.test_generated_sources_root, 
            relative_path(
                get_path_without_extension(farseer_source), 
                project_structure.test_sources_root
            )
        )
        file_system.create_directory_if_missing(directory_name(farseer_cpp_base))

        farseer_cpp_header = farseer_cpp_base + generated_header_file_extension

        farseer_cpp_source = farseer_cpp_base + generated_source_file_extension

        farseer_cpp_headers.append(farseer_cpp_header)

        farseer_cpp_sources.append(farseer_cpp_source)

        file_system.execute_and_fail_on_bad_return(
            [service_executable, service_library, service_name,
             '--protocol', farseer_source,
             '--cpp-header', farseer_cpp_header,
             '--cpp-source', farseer_cpp_source],
            add_to_library_path=[project_structure.external_libraries_root])

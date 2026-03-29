from praline.common import ArtifactPrefix, generated_header_file_extension, generated_source_file_extension
from praline.common.file_system import join, relative_path, get_path_without_extension, directory_name
from praline.common.service import get_service_executable, get_service_library
from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_executables', 'external_libraries', 'main_farseer_sources', 
    ], 
    output=['main_farseer_cpp_headers', 'main_farseer_cpp_sources']
)
def generate_main_farseer_cpp_sources(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    resources         = arguments.resources

    executables     = resources['external_executables']
    libraries       = resources['external_libraries']
    farseer_sources = resources['main_farseer_sources']

    resources['main_farseer_cpp_headers'] = farseer_cpp_headers = []
    resources['main_farseer_cpp_sources'] = farseer_cpp_sources = []

    if arguments.skipOrExceptionIf(
        len(farseer_sources) == 0,
        "There are no main farseer source files the compile"
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
            project_structure.main_generated_sources_root, 
            relative_path(
                get_path_without_extension(farseer_source), 
                project_structure.main_sources_root
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

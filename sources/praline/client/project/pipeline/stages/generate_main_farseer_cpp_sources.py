from praline.common import ArtifactPrefix, header_file_extension, source_file_extension
from praline.common.file_system import join, relative_path, get_path_with_extension, directory_name
from praline.common.service import get_service_executable, get_service_library
from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[
            ['project_directories', 'main_farseer_sources', 'external_executables', 'external_libraries'],
       ], 
       output=['generated_main_farseer_cpp_headers', 'generated_main_farseer_cpp_sources'])
def generate_main_farseer_cpp_sources(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    resources         = arguments.resources

    executable_to_run = artifact_manifest.main_service.executable_to_run
    library_to_load = ArtifactPrefix('dansandu-farseer')

    executables = resources['external_executables']

    libraries = resources['external_libraries']

    service_executable = get_service_executable(executable_to_run, executables)
    service_library = get_service_library(library_to_load, libraries)
    service_name = 'dansandu-farseer-generate_protocol'

    generated_farseer_cpp_headers = []
    generated_farseer_cpp_sources = []

    farseer_sources = resources['main_farseer_sources']
    
    for farseer_source in farseer_sources:
        farseer_cpp_base = join(
            project_structure.main_generated_sources_root, 
            relative_path(get_path_with_extension(farseer_source), project_structure.main_sources_root))
        
        file_system.create_directory_if_missing(directory_name(farseer_cpp_base))
        
        farseer_cpp_header = farseer_cpp_base + header_file_extension

        farseer_cpp_source = farseer_cpp_base + source_file_extension

        generated_farseer_cpp_headers.append(farseer_cpp_header)

        generated_farseer_cpp_sources.append(farseer_cpp_source)

        file_system.execute_and_fail_on_bad_return(
            [service_executable, service_library, service_name,
             '--protocol', farseer_source,
             '--cpp-header', farseer_cpp_header,
             '--cpp-source', farseer_cpp_source],
            add_to_library_path=[project_structure.external_libraries_root])

    resources['generated_main_farseer_cpp_headers'] = generated_farseer_cpp_headers
    resources['generated_main_farseer_cpp_sources'] = generated_farseer_cpp_sources

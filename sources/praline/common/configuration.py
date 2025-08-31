from praline.common import ArtifactDependency, ArtifactManifest, ServiceConfiguration
from praline.common.project_structure import ProjectStructure
from praline.common.compiling.compiler import Compiler, intantiate_compiler
from praline.common.file_system import FileSystem

from typing import Any, Dict


def get_compiler(file_system: FileSystem, program_arguments: Dict[str, Any], pralinefile: Dict[str, Any]) -> Compiler:
    organization = pralinefile['organization']
    artifact     = pralinefile['artifact']
    version      = pralinefile['version']

    mode = program_arguments['global']['mode']
    if mode == None:
        mode = pralinefile['modes'][0]

    architecture = program_arguments['global']['architecture']
    if architecture == None:
        architectures = pralinefile['architectures']
        preferred_architecture = file_system.get_architecture()
        if preferred_architecture in architectures:
            architecture = preferred_architecture
        else:
            architecture = architectures[0]

    platform = program_arguments['global']['platform']
    if platform == None:
        platforms = pralinefile['platforms']
        preferred_platform = file_system.get_platform()
        if preferred_platform in platforms:
            platform = preferred_platform
        else:
            platform = platforms[0]

    exported_symbols = program_arguments['global']['exported_symbols']
    if exported_symbols == None:
        exported_symbols = pralinefile['exported_symbols']

    artifact_type = program_arguments['global']['artifact_type']
    if artifact_type == None:
        artifact_type = pralinefile['artifact_type']

    main_service_executable_to_run = program_arguments['global']['main_service_executable_to_run']
    if main_service_executable_to_run == None:
        main_service_executable_to_run = pralinefile['main_service'].executable_to_run

    main_service_library_to_load = program_arguments['global']['main_service_library_to_load']
    if main_service_library_to_load == None:
        main_service_library_to_load = pralinefile['main_service'].library_to_load

    main_service_name = program_arguments['global']['main_service_name']
    if main_service_name == None:
        main_service_name = pralinefile['main_service'].service_name

    test_service_executable_to_run = program_arguments['global']['test_service_executable_to_run']
    if test_service_executable_to_run == None:
        test_service_executable_to_run = pralinefile['test_service'].executable_to_run

    test_service_library_to_load = program_arguments['global']['test_service_library_to_load']
    if test_service_library_to_load == None:
        test_service_library_to_load = pralinefile['test_service'].library_to_load

    test_service_name = program_arguments['global']['test_service_name']
    if test_service_name == None:
        test_service_name = pralinefile['test_service'].service_name

    dependencies = []
    for dependency in pralinefile['dependencies']:
        dependencies.append(ArtifactDependency(**dependency))

    artifact_manifest = ArtifactManifest(
        organization=organization,
        artifact=artifact,
        version=version,
        mode=mode,
        architecture=architecture,
        platform=platform,
        compiler=None,
        exported_symbols=exported_symbols,
        artifact_type=artifact_type,
        main_service=ServiceConfiguration(
            executable_to_run=main_service_executable_to_run, 
            library_to_load=main_service_library_to_load, 
            service_name=main_service_name
        ),
        test_service=ServiceConfiguration(
            executable_to_run=test_service_executable_to_run, 
            library_to_load=test_service_library_to_load, 
            service_name=test_service_name
        ),
        dependencies=dependencies
    )
    
    project_structure = ProjectStructure(file_system.get_working_directory(), organization, artifact)
    
    compiler_name = program_arguments['global']['compiler']
    fallback_compilers = pralinefile['compilers']
    compiler = intantiate_compiler(
        file_system,
        artifact_manifest, 
        project_structure,
        compiler_name, 
        fallback_compilers
    )

    return compiler

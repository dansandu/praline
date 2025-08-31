from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories', 'main_farseer_sources']], output=[])
def generate_farseer_cpp_sources(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    resources         = arguments.resources

    farseer_prefix = 'dansandu-farseer'
    main_farseer_sources = resources['main_farseer_sources']
    external_executables = resources['external_executables']
    
    

    if main_service_runner_executable == None:
        raise TestServiceRunnerNotSetException(f"Could not find the farseer executable")


    main_sources_root = project_structure.main_sources_root
    resources['main_farseer_sources'] = [
        f for f in file_system.files_in_directory(main_sources_root) if f.endswith('.seer')
    ]

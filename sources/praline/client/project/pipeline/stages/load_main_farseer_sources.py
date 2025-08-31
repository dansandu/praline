from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories']], output=['main_farseer_sources'])
def load_main_farseer_sources(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure
    
    main_sources_root = project_structure.main_sources_root
    resources['main_farseer_sources'] = [
        f for f in file_system.files_in_directory(main_sources_root) if f.endswith('.seer')
    ]

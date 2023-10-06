from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_structure']], output=['main_sources'])
def load_main_sources(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    
    project_structure = resources['project_structure']
    
    resources['main_sources'] = [
        f for f in file_system.files_in_directory(project_structure.sources_root) 
            if f.endswith('.cpp') and not f.endswith('.test.cpp')
    ]

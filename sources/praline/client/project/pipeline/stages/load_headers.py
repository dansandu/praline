from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_structure']], output=['headers'])
def load_headers(arguments: StageArguments):
    file_system = arguments.file_system
    resources   = arguments.resources
    
    project_structure = resources['project_structure']
    sources_root      = project_structure.sources_root
    resources['headers'] = [f for f in file_system.files_in_directory(sources_root) if f.endswith('.hpp')]

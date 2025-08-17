from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import header_file_extension


@stage(requirements=[['project_directories']], output=['main_headers'])
def load_main_headers(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure
    
    main_sources_root = project_structure.main_sources_root
    resources['main_headers'] = [
        f for f in file_system.files_in_directory(main_sources_root) if f.endswith(header_file_extension)
    ]

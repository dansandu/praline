from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories']], output=['headers'])
def load_headers(arguments: StageArguments):
    file_system = arguments.file_system
    resources   = arguments.resources
    compiler    = arguments.compiler
    
    sources_root         = compiler.project_structure.sources_root
    resources['headers'] = [f for f in file_system.files_in_directory(sources_root) if f.endswith('.hpp')]

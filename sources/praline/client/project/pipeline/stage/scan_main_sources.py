from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import files_in_directory


@stage(consumes=['main_sources_root'], produces=['main_sources'])
def scan_main_sources(working_directory, data, cache, arguments):
    data['main_sources'] = [f for f in files_in_directory(data['main_sources_root']) if f.endswith('.cpp') and not f.endswith('.test.cpp')]

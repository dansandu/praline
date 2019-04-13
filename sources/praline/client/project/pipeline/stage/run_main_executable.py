from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import execute_and_fail_on_bad_return


@stage(consumes=['external_libraries_root', 'main_executable', 'resources_root'], exposed=True)
def run_main_executable(working_directory, data, cache, arguments):
    execute_and_fail_on_bad_return([data['main_executable']], add_to_path=[data['external_libraries_root']])

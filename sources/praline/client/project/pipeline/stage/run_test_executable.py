from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import execute_and_fail_on_bad_return, exists


@stage(consumes=['external_libraries_root', 'test_executable'], produces=['test_results'], exposed=True)
def run_test_executable(working_directory, data, cache, arguments):
    execute_and_fail_on_bad_return([data['test_executable']], add_to_path=[data['external_libraries_root']])
    data['test_results'] = 'success'

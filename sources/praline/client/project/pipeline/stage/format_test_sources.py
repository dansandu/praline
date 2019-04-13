from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import execute_and_fail_on_bad_return
from praline.common.hashing import key_delta, hash_file


@stage(consumes=['clang_format_executable', 'test_sources'],
       produces=['formatted_test_sources'],
       cacheable=True)
def format_test_sources(working_directory, data, cache, arguments):
    clang_format_executable = data['clang_format_executable']
    test_sources = data['test_sources']
    
    updated, _, new_cache = key_delta(test_sources, cache, key_hasher=hash_file)
    if updated:
        execute_and_fail_on_bad_return([clang_format_executable, '-i', '-style=file'] + test_sources)
    cache.clear()
    cache.update(new_cache)
    data['formatted_test_sources'] = 'done'

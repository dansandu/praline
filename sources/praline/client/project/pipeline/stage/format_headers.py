from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import execute_and_fail_on_bad_return
from praline.common.hashing import key_delta, hash_file


@stage(consumes=['clang_format_executable', 'headers'],
       produces=['formatted_headers'],
       cacheable=True)
def format_headers(working_directory, data, cache, arguments):
    clang_format_executable = data['clang_format_executable']
    headers = data['headers']
    
    updated, _, new_cache = key_delta(headers, cache, key_hasher=hash_file)
    if updated:
        execute_and_fail_on_bad_return([clang_format_executable, '-i', '-style=file'] + headers)
    cache.clear()
    cache.update(new_cache)
    data['formatted_headers'] = 'done'

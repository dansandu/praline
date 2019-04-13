from praline.client.project.pipeline.stage.base import stage
from praline.common.compiler.base import compile_using_cache
from praline.common.file_system import join


@stage(consumes=['external_headers_root', 'headers_root', 'headers', 'test_sources_root', 'test_sources', 'compiler'],
       produces=['test_objects_root', 'test_objects'],
       cacheable=True)
def compile_test_sources(working_directory, data, cache, arguments):
    header_roots = [data['headers_root'], data['external_headers_root']]
    headers = data['headers']
    sources_root = data['test_sources_root']
    sources = data['test_sources']

    data['test_objects_root'] = objects_root = join(working_directory, 'target', 'objects')
    data['test_objects'] = compile_using_cache(data['compiler'], objects_root, sources_root, sources, header_roots, headers, cache)

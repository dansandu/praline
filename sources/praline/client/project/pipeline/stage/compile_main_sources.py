from praline.client.project.pipeline.stage.base import stage
from praline.common.compiler.base import compile_using_cache
from praline.common.file_system import join


@stage(consumes=['external_headers_root', 'headers_root', 'headers', 'main_sources_root', 'main_sources', 'pralinefile', 'compiler'],
       produces=['main_objects_root', 'main_objects', 'main_executable_object'],
       cacheable=True)
def compile_main_sources(working_directory, data, cache, arguments):
    header_roots = [data['headers_root'], data['external_headers_root']]
    headers = data['headers']
    sources_root = data['main_sources_root']
    sources = data['main_sources']

    pralinefile = data['pralinefile']
    data['main_objects_root'] = objects_root = join(working_directory, 'target', 'objects')
    data['main_objects'] = compile_using_cache(data['compiler'], objects_root, sources_root, sources, header_roots, headers, cache)
    data['main_executable_object'] = join(objects_root, f"{pralinefile['organization']}-{pralinefile['artifact']}-executable.o")

from praline.client.project.pipeline.stage.base import stage
from praline.common.compiler.base import link_library_using_cache
from praline.common.file_system import join
from praline.common.packaging import library_extension


@stage(consumes=['main_objects', 'external_libraries', 'pralinefile', 'compiler', 'platform', 'architecture'],
       produces=['main_library_binary'],
       cacheable=True)
def link_main_library(working_directory, data, cache, arguments):
    pralinefile = data['pralinefile']
    library = f"{pralinefile['organization']}-{pralinefile['artifact']}-{data['architecture']}-{data['platform']}-{data['compiler'].name()}-{pralinefile['version']}{library_extension}"
    data['main_library_binary'] = main_library_binary = join(working_directory, 'target', 'libraries', library)
    link_library_using_cache(data['compiler'], main_library_binary, data['main_objects'], data['external_libraries'], cache)

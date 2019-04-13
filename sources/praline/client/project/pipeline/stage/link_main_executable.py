from praline.client.project.pipeline.stage.base import stage
from praline.common.compiler.base import link_executable_using_cache
from praline.common.file_system import exists, join
from praline.common.packaging import executable_extension


@stage(consumes=['main_executable_object', 'main_objects', 'external_libraries', 'pralinefile', 'architecture', 'platform', 'compiler'],
       produces=['main_executable'],
       cacheable=True)
def link_main_executable(working_directory, data, cache, arguments):
    if not exists(data['main_executable_object']):
        raise RuntimeError('project is not executable -- supply the executable.cpp file to make it executable')
    pralinefile = data['pralinefile']
    executable = f"{pralinefile['organization']}-{pralinefile['artifact']}-{data['architecture']}-{data['platform']}-{data['compiler'].name()}-{pralinefile['version']}{executable_extension}"
    data['main_executable'] = main_executable = join(working_directory, 'target', 'executables', executable)
    link_executable_using_cache(data['compiler'], main_executable, data['main_objects'], data['external_libraries'], cache)

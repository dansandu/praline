from praline.client.project.pipeline.stage.base import stage
from praline.common.compiler.base import link_executable_using_cache
from praline.common.file_system import join
from praline.common.packaging import executable_extension


@stage(consumes=['main_objects', 'main_executable_object', 'test_objects', 'external_libraries', 'pralinefile', 'architecture', 'platform', 'compiler'],
       produces=['test_executable'],
       cacheable=True)
def link_test_executable(working_directory, data, cache, arguments):
    objects = data['main_objects'] + data['test_objects']
    main_executable_object = data['main_executable_object']
    if main_executable_object in objects:
        objects.remove(main_executable_object)

    pralinefile = data['pralinefile']
    executable = f"{pralinefile['organization']}-{pralinefile['artifact']}-{data['architecture']}-{data['platform']}-{data['compiler'].name()}-{pralinefile['version']}.test{executable_extension}"
    data['test_executable'] = test_executable = join(working_directory, 'target', 'executables', executable)
    link_executable_using_cache(data['compiler'], test_executable, objects, data['external_libraries'], cache)

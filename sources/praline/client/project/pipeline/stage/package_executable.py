from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import basename, join, relative_path
from praline.common.packaging import create_package, package_extension


@stage(consumes=['resources_root', 'resources', 'main_executable', 'pralinefile', 'architecture', 'platform', 'compiler'],
       produces=['executable_package'],
       cacheable=True)
def package_executable(working_directory, data, cache, arguments):
    resources_root = data['resources_root']
    resources = data['resources']
    main_executable = data['main_executable']
    
    files_to_package = [(path, join('resources', relative_path(path, resources_root))) for path in resources]
    files_to_package.append((main_executable, basename(main_executable)))
    files_to_package.append((join(working_directory, 'Pralinefile'), 'Pralinefile'))
    directory = join(working_directory, 'target')
    data['executable_package'] = create_package(directory, data['pralinefile'], data['architecture'], data['platform'],
                                                data['compiler'].name(), files_to_package, cache)

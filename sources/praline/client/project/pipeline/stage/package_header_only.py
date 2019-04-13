from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import join, relative_path
from praline.common.packaging import create_package, package_extension


@stage(consumes=['resources_root', 'resources', 'headers_root', 'headers', 'pralinefile', 'architecture', 'platform', 'compiler'],
       produces=['header_only_package'],
       cacheable=True)
def package_header_only(working_directory, data, cache, arguments):
    resources_root = data['resources_root']
    resources = data['resources']
    headers_root = data['headers_root']
    headers = data['headers']
    
    files_to_package = [(path, join('resources', relative_path(path, resources_root))) for path in resources]
    files_to_package.extend((path, join('headers', relative_path(path, headers_root))) for path in headers)
    files_to_package.append((join(working_directory, 'Pralinefile'), 'Pralinefile'))
    directory = join(working_directory, 'target')
    data['header_only_package'] = create_package(directory, data['pralinefile'], data['architecture'], data['platform'],
                                                 data['compiler'].name(), files_to_package, cache)

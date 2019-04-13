from praline.client.project.pipeline.stage.base import stage
from praline.client.repository.remote_proxy import solve_dependencies, pull_package
from praline.common.file_system import create_directory_if_missing, exists, join
from praline.common.hashing import key_delta
from praline.common.packaging import clean_up_package, extract_package, libraries_from_package


@stage(consumes=['pralinefile', 'architecture', 'platform', 'compiler'],
       produces=['external_headers_root', 'external_libraries_root', 'external_libraries'],   
       cacheable=True,
       exposed=True)
def pull_dependencies(working_directory, data, cache, arguments):
    external_root = join(working_directory, 'target', 'external')
    external_package_root = join(external_root, 'packages')

    data['external_libraries_root'] = external_libraries_root = join(external_root, 'libraries')
    data['external_headers_root'] = external_headers_root = join(external_root, 'headers')
    data['external_libraries'] = external_libraries = []
    
    create_directory_if_missing(external_libraries_root)
    create_directory_if_missing(external_headers_root)
    create_directory_if_missing(external_package_root)
    
    packages = solve_dependencies(data['pralinefile'], data['architecture'], data['platform'], data['compiler'].name())
    updated, removed, new_cache = key_delta(packages, cache, key_hasher=lambda k: 0)
    
    for package in removed:
        package_path = join(external_package_root, package)
        clean_up_package(package_path, external_root)

    for package in updated:
        package_path = join(external_package_root, package)
        clean_up_package(package_path, external_root)
        pull_package(package_path)
        external_libraries.extend([join(external_libraries_root, l) for l in extract_package(package_path, external_root)])

    for package in packages:
        if package not in updated:
            package_path = join(external_package_root, package)
            if not exists(package_path):
                pull_package(package_path)
            external_libraries.extend([join(external_libraries_root, l) for l in libraries_from_package(package_path)])

    cache.clear()
    cache.update(new_cache)

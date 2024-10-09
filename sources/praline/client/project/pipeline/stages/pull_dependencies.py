from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import DirectUserMessageException
from praline.common.file_system import join
from praline.common.hashing import DeltaItem, DeltaType, delta, progression_resolution
from praline.common.package import clean_up_package, get_package_contents, unpack

from requests.exceptions import ConnectionError


class PullDependenciesNoConnectionException(DirectUserMessageException):
    pass


@stage(requirements=[['project_directories']],
       output=['external_resources', 'external_headers', 'external_executables', 
               'external_libraries',  'external_libraries_interfaces', 
               'external_symbols_tables'],
       exposed=True,
       has_progress_bar=True)
def pull_dependencies(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    artifact_manifest = arguments.artifact_manifest
    project_structure = arguments.project_structure
    remote_proxy      = arguments.remote_proxy
    cache             = arguments.cache

    progress_bar_supplier = arguments.progress_bar_supplier

    resources['external_resources']            = external_resources            = []
    resources['external_headers']              = external_headers              = []
    resources['external_libraries']            = external_libraries            = []
    resources['external_libraries_interfaces'] = external_libraries_interfaces = []
    resources['external_symbols_tables']       = external_symbols_tables       = []
    resources['external_executables']          = external_executables          = []

    def extend_externals(contents):
        external_resources.extend(contents['resources'])
        external_headers.extend(contents['headers'])
        external_executables.extend(contents['executables'])
        external_libraries.extend(contents['libraries'])
        external_libraries_interfaces.extend(contents['libraries_interfaces'])
        external_symbols_tables.extend(contents['symbols_tables'])

    try:
        package_hashes = remote_proxy.solve_dependencies(artifact_manifest)
    except ConnectionError as exception:
        raise PullDependenciesNoConnectionException(exception)

    external_root = project_structure.external_root
    
    new_cache  = {}
    packages   = package_hashes.keys()
    resolution = progression_resolution(packages, cache)

    hasher = lambda p: package_hashes[p]

    with progress_bar_supplier.create(resolution) as progress_bar:
        def consumer(item: DeltaItem):
            package = item.key
            progress_bar.update_description(package)
            package_path = join(project_structure.external_packages_root, package)

            if item.delta_type == DeltaType.Added:
                remote_proxy.pull_package(package_path)
                contents = unpack(file_system, package_path, external_root)
                extend_externals(contents)

            elif item.delta_type == DeltaType.Modified:
                clean_up_package(file_system, package_path, external_root)
                remote_proxy.pull_package(package_path)
                contents = unpack(file_system, package_path, external_root)
                extend_externals(contents)

            elif item.delta_type == DeltaType.UpToDate:
                if not file_system.exists(package_path):
                    clean_up_package(file_system, package_path, external_root)
                    remote_proxy.pull_package(package_path)
                    contents = unpack(file_system, package_path, external_root)
                    extend_externals(contents)

                else:
                    contents = get_package_contents(file_system, package_path, external_root)
                    extend_externals(contents)

            elif item.delta_type == DeltaType.Removed:
                clean_up_package(file_system, package_path, external_root)

            progress_bar.advance()

        delta(packages, hasher, cache, new_cache, consumer)
            
    
    cache.clear()
    cache.update(new_cache)

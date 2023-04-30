from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join
from praline.common.hashing import delta, DeltaType, progression_resolution
from praline.common.package import clean_up_package, get_package_contents, unpack
from typing import Any, Dict


@stage(requirements=[['project_structure']],
       output=['external_resources', 'external_headers', 'external_executables', 'external_libraries', 
               'external_libraries_interfaces', 'external_symbols_tables'],
       cacheable=True, exposed=True)
def pull_dependencies(file_system: FileSystem, 
                      resources: StageResources, 
                      cache: Dict[str, Any], 
                      program_arguments: Dict[str, Any], 
                      configuration: Dict[str, Any], 
                      remote_proxy: RemoteProxy,
                      progressBarSupplier: ProgressBarSupplier):
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

    artifact_manifest = configuration['artifact_manifest']
    project_structure = resources['project_structure']

    package_hashes = remote_proxy.solve_dependencies(artifact_manifest)
    
    new_cache  = {}
    packages   = package_hashes.keys()
    resolution = progression_resolution(packages, cache)
    with progressBarSupplier.create(resolution) as progress_bar:
        for item in delta(packages, lambda p: package_hashes[p], cache, new_cache):
            package = item.key
            progress_bar.update_summary(package)
            package_path = join(project_structure.external_packages_root, package)
            if item.delta_type == DeltaType.Added:
                remote_proxy.pull_package(package_path)
                contents = unpack(file_system, package_path, project_structure.external_root)
                extend_externals(contents)
            elif item.delta_type == DeltaType.Modified:
                clean_up_package(file_system, package_path, project_structure.external_root)
                remote_proxy.pull_package(package_path)
                contents = unpack(file_system, package_path, project_structure.external_root)
                extend_externals(contents)
            elif item.delta_type == DeltaType.UpToDate:
                if not file_system.exists(package_path):
                    clean_up_package(file_system, package_path, project_structure.external_root)
                    remote_proxy.pull_package(package_path)
                    contents = unpack(file_system, package_path, project_structure.external_root)
                    extend_externals(contents)
                else:
                    contents = get_package_contents(file_system, package_path, project_structure.external_root)
                    extend_externals(contents)
            elif item.delta_type == DeltaType.Removed:
                clean_up_package(file_system, package_path, project_structure.external_root)
            progress_bar.advance()
    
    cache.clear()
    cache.update(new_cache)

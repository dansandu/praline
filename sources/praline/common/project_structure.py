from praline.common.yield_descriptor import IYieldDescriptor
from praline.common.file_system import join, relative_path
from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectStructure:
    project_directory: str
    resources_root: str
    resources_domain_root: str
    sources_root: str
    sources_domain_root: str
    target_root: str
    objects_root: str
    executables_root: str
    libraries_root: str
    libraries_interfaces_root: str
    symbols_tables_root: str
    temporary_root: str
    external_root: str
    external_packages_root: str
    external_headers_root: str
    external_executables_root: str
    external_libraries_root: str
    external_libraries_interfaces_root: str
    external_symbols_tables_root: str

    def get_object_path(self, yield_descriptor: IYieldDescriptor, source_path: str) -> str:
        source_relative_path = relative_path(source_path, self.sources_root)
        return join(self.objects_root, yield_descriptor.get_object(source_relative_path))

    def get_executable_path(self, yield_descriptor: IYieldDescriptor, artifact_identifier: str) -> str:
        return join(self.executables_root, yield_descriptor.get_executable(artifact_identifier))

    def get_library_path(self, yield_descriptor: IYieldDescriptor, artifact_identifier: str) -> str:
        return join(self.libraries_root, yield_descriptor.get_library(artifact_identifier))
    
    def get_library_interface_path(self, yield_descriptor: IYieldDescriptor, artifact_identifier: str) -> str:
        return join(self.libraries_interfaces_root, yield_descriptor.get_library_interface(artifact_identifier))

    def get_symbols_table_path(self, yield_descriptor: IYieldDescriptor, artifact_identifier: str) -> str:
        return join(self.symbols_tables_root, yield_descriptor.get_symbols_table(artifact_identifier))


def get_project_structure(project_directory: str, organization: str, artifact: str) -> ProjectStructure:
    target_root       = join(project_directory, 'target')
    external_root     = join(target_root, 'external')

    resources_root = join(project_directory, 'resources')
    sources_root   = join(project_directory, 'sources')

    project_structure = ProjectStructure(
        project_directory=project_directory,
        resources_root=resources_root,
        resources_domain_root=join(resources_root, organization, artifact),
        sources_root=sources_root,
        sources_domain_root=join(sources_root, organization, artifact),
        target_root=target_root,
        objects_root=join(target_root, 'objects'),
        executables_root=join(target_root, 'executables'),
        libraries_root=join(target_root, 'libraries'),
        libraries_interfaces_root=join(target_root, 'libraries_interfaces'),
        symbols_tables_root=join(target_root, 'symbols_tables'),
        temporary_root=join(target_root, 'temporary'),
        external_root=external_root,
        external_packages_root=join(external_root, 'packages'),
        external_headers_root=join(external_root, 'headers'),
        external_executables_root=join(external_root, 'executables'),
        external_libraries_root=join(external_root, 'libraries'),
        external_libraries_interfaces_root=join(external_root, 'libraries_interfaces'),
        external_symbols_tables_root=join(external_root, 'symbols_tables')
    )
    
    return project_structure

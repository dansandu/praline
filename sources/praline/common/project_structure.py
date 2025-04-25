from praline.common.yield_descriptor import IYieldDescriptor
from praline.common.file_system import join, relative_path
from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectStructure:
    project_directory: str

    resources_root: str

    main_resources_root: str
    main_resources_domain_root: str
    main_sources_root: str
    main_sources_domain_root: str

    test_resources_root: str
    test_resources_domain_root: str
    test_sources_root: str
    test_sources_domain_root: str

    target_root: str
    main_objects_root: str
    test_objects_root: str
    executables_root: str
    libraries_root: str
    libraries_interfaces_root: str
    symbols_tables_root: str
    packages_root: str
    temporary_root: str

    external_root: str
    external_packages_root: str
    external_headers_root: str
    external_executables_root: str
    external_libraries_root: str
    external_libraries_interfaces_root: str
    external_symbols_tables_root: str

    def get_main_object_path(self, yield_descriptor: IYieldDescriptor, main_source_path: str) -> str:
        main_source_relative_path = relative_path(main_source_path, self.main_sources_root)
        return join(self.main_objects_root, yield_descriptor.get_object(main_source_relative_path))
    
    def get_test_object_path(self, yield_descriptor: IYieldDescriptor, test_source_path: str) -> str:
        test_source_relative_path = relative_path(test_source_path, self.test_sources_root)
        return join(self.test_objects_root, yield_descriptor.get_object(test_source_relative_path))

    def get_executable_and_symbols_table_path(self, yield_descriptor: IYieldDescriptor, artifact_identifier: str) -> str:
        executable, symbols_table = yield_descriptor.get_executable_and_symbols_table(artifact_identifier)
        if symbols_table:
            return (join(self.executables_root, executable), join(self.symbols_tables_root, symbols_table))
        else:
            return (join(self.executables_root, executable), None)

    def get_library_and_symbols_table_path(self, yield_descriptor: IYieldDescriptor, artifact_identifier: str) -> str:
        library, symbols_table = yield_descriptor.get_library_and_symbols_table(artifact_identifier)
        if symbols_table:
            return (join(self.libraries_root, library), join(self.symbols_tables_root, symbols_table))
        else:
            return (join(self.libraries_root, library), None)
    
    def get_library_interface_path(self, yield_descriptor: IYieldDescriptor, artifact_identifier: str) -> str:
        return join(self.libraries_interfaces_root, yield_descriptor.get_library_interface(artifact_identifier))


def get_project_structure(project_directory: str, organization: str, artifact: str) -> ProjectStructure:

    resources_root = join(project_directory, 'resources')
    sources_root   = join(project_directory, 'sources')
    target_root    = join(project_directory, 'target')
    external_root  = join(target_root, 'external')

    main = 'main'
    test = 'test'

    project_structure = ProjectStructure(
        project_directory = project_directory,

        resources_root = resources_root,

        main_resources_root        = join(resources_root, main),
        main_resources_domain_root = join(resources_root, main, organization, artifact),
        main_sources_root          = join(sources_root,   main),
        main_sources_domain_root   = join(sources_root,   main, organization, artifact),

        test_resources_root        = join(resources_root, test),
        test_resources_domain_root = join(resources_root, test, organization, artifact),
        test_sources_root          = join(sources_root,   test),
        test_sources_domain_root   = join(sources_root,   test, organization, artifact),

        target_root               = target_root,
        main_objects_root         = join(target_root, 'objects', main),
        test_objects_root         = join(target_root, 'objects', test),
        executables_root          = join(target_root, 'executables'),
        libraries_root            = join(target_root, 'libraries'),
        libraries_interfaces_root = join(target_root, 'libraries_interfaces'),
        symbols_tables_root       = join(target_root, 'symbols_tables'),
        packages_root             = join(target_root, 'packages'),
        temporary_root            = join(target_root, 'temporary'),

        external_root                      = external_root,
        external_packages_root             = join(external_root, 'packages'),
        external_headers_root              = join(external_root, 'headers'),
        external_executables_root          = join(external_root, 'executables'),
        external_libraries_root            = join(external_root, 'libraries'),
        external_libraries_interfaces_root = join(external_root, 'libraries_interfaces'),
        external_symbols_tables_root       = join(external_root, 'symbols_tables')
    )
    
    return project_structure

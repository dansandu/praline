from praline.common.yield_descriptor import IYieldDescriptor
from praline.common.file_system import is_subpath, join, relative_path


class ProjectStructure:
    def __init__(self, project_directory, organization, artifact):
        self.project_directory = project_directory

        main = 'main'
        test = 'test'

        self.sources_root = join(self.project_directory, 'sources')

        self.resources_root = join(self.project_directory, 'resources')

        self.main_resources_root        = join(self.resources_root, main)
        self.main_resources_domain_root = join(self.resources_root, main, organization, artifact)

        self.main_sources_root          = join(self.sources_root, main)
        self.main_sources_domain_root   = join(self.sources_root, main, organization, artifact)

        self.test_resources_root        = join(self.resources_root, test)
        self.test_resources_domain_root = join(self.resources_root, test, organization, artifact)

        self.test_sources_root        = join(self.sources_root, test)
        self.test_sources_domain_root = join(self.sources_root, test, organization, artifact)

        self.target_root       = join(self.project_directory, 'target')
        self.main_objects_root = join(self.target_root,       'objects', main)
        self.test_objects_root = join(self.target_root,       'objects', test)

        self.generated_root              = join(self.target_root,    'generated')
        self.main_generated_sources_root = join(self.generated_root, 'sources', main)
        self.test_generated_sources_root = join(self.generated_root, 'sources', test)

        self.executables_root          = join(self.target_root, 'executables')
        self.packages_root             = join(self.target_root, 'packages')
        self.libraries_root            = join(self.target_root, 'libraries')
        self.libraries_interfaces_root = join(self.target_root, 'libraries_interfaces')
        self.symbols_tables_root       = join(self.target_root, 'symbols_tables')
        self.temporary_root            = join(self.target_root, 'temporary')

        self.external_root                      = join(self.target_root,   'external')
        self.external_packages_root             = join(self.external_root, 'packages')
        self.external_headers_root              = join(self.external_root, 'headers')
        self.external_executables_root          = join(self.external_root, 'executables')
        self.external_libraries_root            = join(self.external_root, 'libraries')
        self.external_libraries_interfaces_root = join(self.external_root, 'libraries_interfaces')
        self.external_symbols_tables_root       = join(self.external_root, 'symbols_tables')

    def get_main_object_path(self, yield_descriptor: IYieldDescriptor, main_source_path: str) -> str:
        if is_subpath(self.main_generated_sources_root, main_source_path):
            main_source_relative_path = relative_path(main_source_path, self.main_generated_sources_root)
        else:
            main_source_relative_path = relative_path(main_source_path, self.main_sources_root)

        return join(self.main_objects_root, yield_descriptor.get_object(main_source_relative_path))
    
    def get_test_object_path(self, yield_descriptor: IYieldDescriptor, test_source_path: str) -> str:
        if is_subpath(self.test_generated_sources_root, test_source_path):
            test_source_relative_path = relative_path(test_source_path, self.test_generated_sources_root)
        else:
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

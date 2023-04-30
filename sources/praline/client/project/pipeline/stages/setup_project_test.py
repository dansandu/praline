from os.path import normpath
from praline.client.project.pipeline.stages.setup_project import setup_project, IllformedProjectError
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform)
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class SetupProjectStageTest(TestCase):
    def setUp(self):
        self.configuration = {
            'artifact_manifest': ArtifactManifest(organization='my_organization',
                                                  artifact='my_artifact',
                                                  version=ArtifactVersion.from_string('0.0.0'),
                                                  mode=Mode.debug,
                                                  architecture=Architecture.arm,
                                                  platform=Platform.linux,
                                                  compiler=Compiler.gcc,
                                                  exported_symbols=ExportedSymbols.explicit,
                                                  artifact_type=ArtifactType.executable,
                                                  artifact_logging_level=ArtifactLoggingLevel.debug,
                                                  dependencies=[]) 
        }

    def test_project_setup(self):
        file_system = FileSystemMock(
            directories={
                'my/project',
            },
            working_directory='my/project'
        )

        resources = {}

        setup_project(file_system, resources, None, None, self.configuration, None, None)

        expected_directories = {
            'my/project/resources/my_organization/my_artifact',
            'my/project/sources/my_organization/my_artifact',
            'my/project/target/objects',
            'my/project/target/executables',
            'my/project/target/libraries',
            'my/project/target/libraries_interfaces',
            'my/project/target/symbols_tables',
            'my/project/target/external/packages',
            'my/project/target/external/headers',
            'my/project/target/external/executables',
            'my/project/target/external/libraries',
            'my/project/target/external/libraries_interfaces',
            'my/project/target/external/symbols_tables',
        }

        self.assertEqual(file_system.directories, {normpath(p) for p in expected_directories})

        self.assertIn('project_structure', resources)

        expected_project_structure = {
            'project_directory': 'my/project',
            'resources_root': 'my/project/resources',
            'sources_root': 'my/project/sources',
            'objects_root': 'my/project/target/objects',
            'executables_root': 'my/project/target/executables',
            'libraries_root': 'my/project/target/libraries',
            'libraries_interfaces_root': 'my/project/target/libraries_interfaces',
            'symbols_tables_root': 'my/project/target/symbols_tables',
            'external_root': 'my/project/target/external',
            'external_packages_root': 'my/project/target/external/packages',
            'external_headers_root': 'my/project/target/external/headers',
            'external_executables_root': 'my/project/target/external/executables',
            'external_libraries_root': 'my/project/target/external/libraries',
            'external_libraries_interfaces_root': 'my/project/target/external/libraries_interfaces',
            'external_symbols_tables_root': 'my/project/target/external/symbols_tables',
        }

        project_structure = resources['project_structure']

        for key, path in expected_project_structure.items():
            self.assertEqual(normpath(getattr(project_structure, key)), normpath(path))

    def test_invalid_project_resources(self):        
        file_system = FileSystemMock(
            directories={
                'my/project/resources/my_organization/my_artifact',
                'my/project/sources/my_organization/my_artifact'
            },
            files={
                'my/project/resources/my_organization/somefile': b''
            },
            working_directory='my/project'
        )

        resources = {}

        self.assertRaises(IllformedProjectError, 
                          setup_project, file_system, resources, None, None, self.configuration, None, None)

    def test_invalid_project_sources(self):
        file_system = FileSystemMock(
            directories={
                'my/project/resources/my_organization/my_artifact',
                'my/project/sources/my_organization/my_artifact'
            }, 
            files={
                'my/project/sources/somefile': b''
            },
            working_directory='my/project'
        )

        resources = {}

        self.assertRaises(IllformedProjectError, 
                          setup_project, file_system, resources, None, None, self.configuration, None, None)

    def test_valid_project_with_hidden_file(self):
        file_system = FileSystemMock(
            directories={
                'my/project/resources/my_organization/my_artifact',
                'my/project/sources/my_organization/my_artifact'
            },
            files={
                'my/project/sources/.hidden': b''
            },
            working_directory='my/project'
        )

        resources = {}

        setup_project(file_system, resources, None, None, self.configuration, None, None)

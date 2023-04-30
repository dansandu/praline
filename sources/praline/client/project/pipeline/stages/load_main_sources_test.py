from os.path import normpath
from praline.client.project.pipeline.stages.load_main_sources import (load_main_sources, main_executable_contents, 
                                                                      ExecutableFileWithLibraryError)
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform, ProjectStructure)
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadMainSourcesStageTest(TestCase):
    def test_load_main_sources(self):
        file_system = FileSystemMock(
            directories={
                'project/resources/org/art',
                'project/sources/org/art'
            }, 
            files={
                'project/resources/org/art/generated.cpp': b'',
                'project/sources/org/art/math.hpp': b'',
                'project/sources/org/art/math.cpp': b'',
                'project/sources/org/art/math.test.cpp': b''
            }
        )

        resources = {
            'project_structure': ProjectStructure(
                project_directory='project',
                resources_root='project/resources',
                sources_root='project/sources',
                target_root='project/target',
                objects_root='project/target/objects',
                executables_root='project/target/executables',
                libraries_root='project/target/libraries',
                libraries_interfaces_root='project/target/libraries_interfaces',
                symbols_tables_root='project/target/symbols_tables',
                external_root='project/target/external',
                external_packages_root='project/target/external/packages',
                external_headers_root='project/target/external/headers',
                external_executables_root='project/target/external/executables',
                external_libraries_root='project/target/external/libraries',
                external_libraries_interfaces_root='project/target/external/libraries_interfaces',
                external_symbols_tables_root='project/target/external/symbols_tables'
            ),    
        }

        configuration = {
            'artifact_manifest': ArtifactManifest(organization='org',
                                                  artifact='art',
                                                  version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
                                                  mode=Mode.debug,
                                                  architecture=Architecture.arm,
                                                  platform=Platform.linux,
                                                  compiler=Compiler.gcc,
                                                  exported_symbols=ExportedSymbols.explicit,
                                                  artifact_type=ArtifactType.library,
                                                  artifact_logging_level=ArtifactLoggingLevel.debug,
                                                  dependencies=[])  
        }

        load_main_sources(file_system, resources, None, None, configuration, None, None)

        expected_main_sources = {
            'project/sources/org/art/math.cpp'
        }

        self.assertEqual({normpath(p) for p in resources['main_sources']},
                         {normpath(p) for p in expected_main_sources})

    def test_load_main_sources_with_executable(self):
        file_system = FileSystemMock({'project/sources/org/art'})

        resources = {
            'project_structure': ProjectStructure(
                project_directory='project',
                resources_root='project/resources',
                sources_root='project/sources',
                target_root='project/target',
                objects_root='project/target/objects',
                executables_root='project/target/executables',
                libraries_root='project/target/libraries',
                libraries_interfaces_root='project/target/libraries_interfaces',
                symbols_tables_root='project/target/symbols_tables',
                external_root='project/target/external',
                external_packages_root='project/target/external/packages',
                external_headers_root='project/target/external/headers',
                external_executables_root='project/target/external/executables',
                external_libraries_root='project/target/external/libraries',
                external_libraries_interfaces_root='project/target/external/libraries_interfaces',
                external_symbols_tables_root='project/target/external/symbols_tables'
            ),    
        }

        configuration = {
            'artifact_manifest': ArtifactManifest(organization='org',
                                                  artifact='art',
                                                  version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
                                                  mode=Mode.debug,
                                                  architecture=Architecture.arm,
                                                  platform=Platform.linux,
                                                  compiler=Compiler.gcc,
                                                  exported_symbols=ExportedSymbols.explicit,
                                                  artifact_type=ArtifactType.executable,
                                                  artifact_logging_level=ArtifactLoggingLevel.debug,
                                                  dependencies=[])  
        }

        load_main_sources(file_system, resources, None, None, configuration, None, None)

        expected_files = {
            'project/sources/org/art/executable.cpp': main_executable_contents.encode('utf-8')
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in expected_files.items()})

        self.assertEqual(normpath(resources['main_executable_source']),
                         normpath('project/sources/org/art/executable.cpp'))

        expected_main_sources = {
            'project/sources/org/art/executable.cpp'
        }

        self.assertEqual({normpath(p) for p in resources['main_sources']},
                         {normpath(p) for p in expected_main_sources})

    def test_invalid_library_with_executable(self):
        file_system = FileSystemMock(
            directories={
                'project/resources/org/art',
                'project/sources/org/art'
            }, 
            files={
                'project/sources/org/art/executable.cpp': b'',
                'project/sources/org/art/executable.test.cpp': b''
            }
        )

        resources = {
            'project_structure': ProjectStructure(
                project_directory='project',
                resources_root='project/resources',
                sources_root='project/sources',
                target_root='project/target',
                objects_root='project/target/objects',
                executables_root='project/target/executables',
                libraries_root='project/target/libraries',
                libraries_interfaces_root='project/target/libraries_interfaces',
                symbols_tables_root='project/target/symbols_tables',
                external_root='project/target/external',
                external_packages_root='project/target/external/packages',
                external_headers_root='project/target/external/headers',
                external_executables_root='project/target/external/executables',
                external_libraries_root='project/target/external/libraries',
                external_libraries_interfaces_root='project/target/external/libraries_interfaces',
                external_symbols_tables_root='project/target/external/symbols_tables'
            ),    
        }

        configuration = {
            'artifact_manifest': ArtifactManifest(organization='org',
                                                  artifact='art',
                                                  version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
                                                  mode=Mode.debug,
                                                  architecture=Architecture.arm,
                                                  platform=Platform.linux,
                                                  compiler=Compiler.gcc,
                                                  exported_symbols=ExportedSymbols.explicit,
                                                  artifact_type=ArtifactType.library,
                                                  artifact_logging_level=ArtifactLoggingLevel.debug,
                                                  dependencies=[])  
        }

        self.assertRaises(ExecutableFileWithLibraryError, 
                          load_main_sources, file_system, resources, None, None, configuration, None, None)

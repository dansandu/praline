from praline.client.project.pipeline.stages.stage import StageArguments
from praline.client.project.pipeline.stages.load_main_sources import (load_main_sources, main_executable_contents, 
                                                                      ExecutableFileWithLibraryError)
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform, ProjectStructure)
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadMainSourcesStageTest(TestCase):
    def test_load_main_sources(self):
        file_system = FileSystemMock(
            directories={
                join('project', 'resources', 'org', 'art'),
                join('project', 'sources', 'org', 'art'),
            }, 
            files={
                join('project', 'resources', 'org', 'art', 'generated.cpp'): b'',
                join('project', 'sources', 'org', 'art', 'math.hpp'): b'',
                join('project', 'sources', 'org', 'art', 'math.cpp'): b'',
                join('project', 'sources', 'org', 'art', 'math.test.cpp'): b'',
            },
            working_directory='project',
        )

        resources = {
            'project_structure': project_structure_dummy,    
        }

        artifact_manifest = ArtifactManifest(organization='org',
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

        stage_arguments = StageArguments(file_system=file_system,
                                         artifact_manifest=artifact_manifest,
                                         resources=resources)

        load_main_sources(stage_arguments)

        expected_main_sources = {
            join('project', 'sources', 'org', 'art', 'math.cpp')
        }

        self.assertCountEqual(resources['main_sources'], expected_main_sources)

    def test_load_main_sources_with_executable(self):
        file_system = FileSystemMock(
            directories={'project'}, 
            working_directory='project',
        )

        resources = {
            'project_structure': project_structure_dummy,    
        }

        artifact_manifest = ArtifactManifest(organization='org',
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

        stage_arguments = StageArguments(file_system=file_system,
                                         artifact_manifest=artifact_manifest,
                                         resources=resources)

        load_main_sources(stage_arguments)

        main_executable_source = join('project', 'sources', 'org', 'art', 'executable.cpp')

        expected_files = {
            main_executable_source: main_executable_contents.encode('utf-8'),
        }

        self.assertCountEqual(file_system.files, expected_files)

        self.assertEqual(resources['main_executable_source'], main_executable_source)

        expected_main_sources = {
            main_executable_source,
        }

        self.assertCountEqual(resources['main_sources'], expected_main_sources)

    def test_invalid_library_with_executable(self):
        file_system = FileSystemMock(
            directories={
                join('project', 'resources', 'org', 'art'),
                join('project', 'sources', 'org', 'art'),
            }, 
            files={
                join('project', 'sources', 'org', 'art', 'executable.cpp'): b'',
                join('project', 'sources', 'org', 'art', 'executable.test.cpp'): b'',
            },
            working_directory='project',
        )

        resources = {
            'project_structure': project_structure_dummy,    
        }

        artifact_manifest = ArtifactManifest(organization='org',
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
        
        stage_arguments = StageArguments(file_system=file_system,
                                         artifact_manifest=artifact_manifest,
                                         resources=resources)

        self.assertRaises(ExecutableFileWithLibraryError, 
                          load_main_sources, stage_arguments)

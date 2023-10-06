from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_test_sources import load_test_sources, test_executable_contents
from praline.client.project.pipeline.stages import StageArguments
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform)
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadTestSourcesStageTest(TestCase):
    def test_load_test_sources(self):
        header_math = join('project', 'sources', 'org', 'art', 'math.hpp')
        source_math = join('project', 'sources', 'org', 'art', 'math.cpp')
        test_math   = join('project', 'sources', 'org', 'art', 'math.test.cpp')
        test_main   = join('project', 'sources', 'org', 'art', 'executable.test.cpp')


        file_system = FileSystemMock(
            directories={
                join('project', 'sources', 'org', 'art'),
            },
            files={
                header_math: b'',
                source_math: b'',
                test_math: b'',
            },
            working_directory='project',
        )

        artifact_manifest = ArtifactManifest(organization='org',
                                             artifact='art',
                                             version=ArtifactVersion.from_string('5.35.5.SNAPSHOT'),
                                             mode=Mode.debug,
                                             architecture=Architecture.arm,
                                             platform=Platform.linux,
                                             compiler=Compiler.gcc,
                                             exported_symbols=ExportedSymbols.explicit,
                                             artifact_type=ArtifactType.library,
                                             artifact_logging_level=ArtifactLoggingLevel.debug,
                                             dependencies=[])      
        
        with StageResources(stage='load_test_sources', 
                            activation=0, 
                            resources={'project_structure': project_structure_dummy}, 
                            constrained_output=['test_sources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, 
                                             artifact_manifest=artifact_manifest, 
                                             resources=resources)
            load_test_sources(stage_arguments)

        expected_test_sources = {
            test_math,
            test_main,
        }

        self.assertCountEqual(resources['test_sources'], expected_test_sources)

        expected_files = {
            header_math: b'',
            source_math: b'',
            test_math: b'',
            test_main: test_executable_contents.encode('utf-8')
        }

        self.assertEqual(file_system.files, expected_files)

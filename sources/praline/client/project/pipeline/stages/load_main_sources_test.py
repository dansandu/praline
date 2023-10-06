from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.load_main_sources import load_main_sources
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform)
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

        with StageResources(stage='load_main_sources', 
                            activation=0, 
                            resources={'project_structure': project_structure_dummy}, 
                            constrained_output=['main_sources']) as resources:
            stage_arguments = StageArguments(file_system=file_system,
                                             artifact_manifest=artifact_manifest,
                                             resources=resources)
            load_main_sources(stage_arguments)

        expected_main_sources = {
            join('project', 'sources', 'org', 'art', 'math.cpp')
        }

        self.assertCountEqual(resources['main_sources'], expected_main_sources)

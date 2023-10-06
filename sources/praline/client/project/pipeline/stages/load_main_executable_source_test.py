from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.load_main_executable_source import load_main_executable_source, main_executable_source_contents
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform)
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadMainExecutableSourceStageTest(TestCase):
    def test_load_main_executable_source(self):
        file_system = FileSystemMock(
            directories={'project'}, 
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
                                             artifact_type=ArtifactType.executable,
                                             artifact_logging_level=ArtifactLoggingLevel.debug,
                                             dependencies=[])  

        with StageResources(stage='load_main_executable_source', 
                            activation=0, 
                            resources={'project_structure': project_structure_dummy},
                            constrained_output=['main_executable_source']) as resources:
            stage_arguments = StageArguments(file_system=file_system,
                                             artifact_manifest=artifact_manifest,
                                             resources=resources)
            load_main_executable_source(stage_arguments)

        main_executable_source = join('project', 'sources', 'org', 'art', 'executable.cpp')

        expected_files = {
            main_executable_source: main_executable_source_contents.encode('utf-8'),
        }

        self.assertCountEqual(file_system.files, expected_files)

        self.assertEqual(resources['main_executable_source'], main_executable_source)

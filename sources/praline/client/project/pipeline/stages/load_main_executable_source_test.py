from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments
from praline.client.project.pipeline.stages.load_main_executable_source import load_main_executable_source, main_executable_source_contents, predicate
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform, executable_source_file_name)
from praline.common.project_structure import get_project_structure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadMainExecutableSourceStageTest(TestCase):
    def test_load_main_executable_source(self):
        artifact_manifest = ArtifactManifest(organization='org',
                                             artifact='art',
                                             version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
                                             mode=Mode.debug,
                                             architecture=Architecture.arm,
                                             platform=Platform.linux,
                                             compiler=CompilerType.gcc,
                                             exported_symbols=ExportedSymbols.explicit,
                                             artifact_type=ArtifactType.executable,
                                             test_service_runner=None,
                                             test_service_name='default',
                                             dependencies=[])  

        project_structure = get_project_structure('project', artifact_manifest.organization, artifact_manifest.artifact)

        file_system = FileSystemMock(
            directories={
                project_structure.project_directory
            }, 
            working_directory=project_structure.project_directory,
        )

        predicate_result = predicate(StagePredicateArguments(artifact_manifest=artifact_manifest))

        self.assertTrue(predicate_result.can_run)

        with StageResources(stage='load_main_executable_source', 
                            activation=0, 
                            resources={'project_structure': True},
                            constrained_output=['main_executable_source']) as resources:
            stage_arguments = StageArguments(file_system=file_system, project_structure=project_structure, resources=resources)
            load_main_executable_source(stage_arguments)

        main_executable_source = join(project_structure.main_sources_domain_root, executable_source_file_name)

        expected_files = {
            main_executable_source: main_executable_source_contents.encode('utf-8'),
        }

        self.assertCountEqual(file_system.files, expected_files)

        self.assertEqual(resources['main_executable_source'], main_executable_source)

    def test_load_main_executable_source_as_library(self):
        artifact_manifest = ArtifactManifest(organization='org',
                                             artifact='art',
                                             version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
                                             mode=Mode.debug,
                                             architecture=Architecture.arm,
                                             platform=Platform.linux,
                                             compiler=CompilerType.gcc,
                                             exported_symbols=ExportedSymbols.explicit,
                                             artifact_type=ArtifactType.library,
                                             test_service_runner=None,
                                             test_service_name='default',
                                             dependencies=[]) 
        
        predicate_result = predicate(StagePredicateArguments(artifact_manifest=artifact_manifest))

        self.assertFalse(predicate_result.can_run)

        self.assertGreater(len(predicate_result.explanation), 0)

from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments
from praline.client.project.pipeline.stages.load_test_executable_source import load_test_executable_source, predicate
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform, test_executable_source_file_name)
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadTestExecutableSourceStageTest(TestCase):
    def test_load_test_executable_source(self):
        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
            mode=Mode.debug,
            architecture=Architecture.arm,
            platform=Platform.linux,
            compiler=CompilerType.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.executable,
            main_service=None,
            test_service=None,
            dependencies=[]
        )  

        project_structure = ProjectStructure('project', artifact_manifest.organization, artifact_manifest.artifact)

        test_executable_source = join(project_structure.test_sources_domain_root, test_executable_source_file_name)

        file_system = FileSystemMock(
            directories={
                project_structure.project_directory,
                project_structure.test_sources_domain_root,
            },
            files={
                test_executable_source: b'',
            },
            working_directory=project_structure.project_directory,
        )

        stage_predicate_arguments = StagePredicateArguments(
            artifact_manifest=artifact_manifest,
            file_system=file_system,
            project_structure=project_structure)

        predicate_result = predicate(stage_predicate_arguments)

        self.assertTrue(predicate_result.can_run)

        with StageResources(stage='load_test_executable_source', 
                            activation=0, 
                            resources={'project_structure': True},
                            constrained_output=['test_executable_source']) as resources:
            stage_arguments = StageArguments(
                file_system=file_system, 
                project_structure=project_structure, 
                resources=resources)
            
            load_test_executable_source(stage_arguments)

        self.assertEqual(resources['test_executable_source'], test_executable_source)

    def test_load_test_executable_with_no_source(self):
        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
            mode=Mode.debug,
            architecture=Architecture.arm,
            platform=Platform.linux,
            compiler=CompilerType.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.library,
            main_service=None,
            test_service=None,
            dependencies=[]
        ) 

        project_structure = ProjectStructure('project', artifact_manifest.organization, artifact_manifest.artifact)

        file_system = FileSystemMock(
            directories={
                project_structure.project_directory,
                project_structure.test_sources_domain_root,
            },
            working_directory=project_structure.project_directory,
        )
        
        stage_predicate_arguments = StagePredicateArguments(
            artifact_manifest=artifact_manifest,
            file_system=file_system,
            project_structure=project_structure)

        predicate_result = predicate(stage_predicate_arguments)

        self.assertFalse(predicate_result.can_run)

        self.assertGreater(len(predicate_result.explanation), 0)

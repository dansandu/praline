from praline.client.project.pipeline.stage_resources import DeclaredResourceNotSuppliedError, StageResources
from praline.client.project.pipeline.stages.setup_project import setup_project, IllformedProjectError
from praline.client.project.pipeline.stages import StageArguments
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform)
from praline.common.project_structure import get_project_structure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class SetupProjectStageTest(TestCase):
    def setUp(self):
        organization = 'my_organization'
        artifact = 'my_artifact'

        self.artifact_manifest = ArtifactManifest(organization=organization,
                                                  artifact=artifact,
                                                  version=ArtifactVersion.from_string('0.0.0'),
                                                  mode=Mode.debug,
                                                  architecture=Architecture.arm,
                                                  platform=Platform.linux,
                                                  compiler=CompilerType.gcc,
                                                  exported_symbols=ExportedSymbols.explicit,
                                                  artifact_type=ArtifactType.executable,
                                                  test_service_runner=None,
                                                  test_service_name='default',
                                                  dependencies=[])
        
        self.project_structure = get_project_structure(project_directory='directory', organization=organization, artifact=artifact)

    def test_project_setup(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.project_directory,
            },
            working_directory=self.project_structure.project_directory
        )

        with StageResources(stage='setup_project', 
                            activation=0, 
                            resources={}, 
                            constrained_output=['project_directories']) as resources:
            stage_arguments = StageArguments(file_system=file_system, 
                                             project_structure=self.project_structure, 
                                             artifact_manifest=self.artifact_manifest, 
                                             resources=resources)
            setup_project(stage_arguments)

        self.assertTrue(resources['project_directories'])

        for path in vars(self.project_structure).values():
            self.assertTrue(file_system.is_directory(path))

    def test_invalid_project_resources(self):        
        file_system = FileSystemMock(
            directories={
                self.project_structure.project_directory,
                self.project_structure.main_resources_domain_root,
                self.project_structure.main_sources_domain_root,
            },
            files={
                join(self.project_structure.main_resources_root, self.artifact_manifest.organization, 'somefile'): b''
            },
            working_directory=self.project_structure.project_directory
        )

        try:
            with StageResources(stage='setup_project', 
                                activation=0, 
                                resources={}, 
                                constrained_output=['project_directories']) as resources:
                stage_arguments = StageArguments(file_system=file_system, 
                                                 project_structure=self.project_structure, 
                                                 artifact_manifest=self.artifact_manifest, 
                                                 resources=resources)
                self.assertRaises(IllformedProjectError, setup_project, stage_arguments)
        except DeclaredResourceNotSuppliedError:
            pass

    def test_invalid_project_sources(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.project_directory,
                self.project_structure.main_resources_domain_root,
                self.project_structure.main_sources_domain_root,
            }, 
            files={
                join(self.project_structure.main_sources_root, 'somefile'): b''
            },
            working_directory=self.project_structure.project_directory
        )

        try:
            with StageResources(stage='setup_project', 
                                activation=0, 
                                resources={}, 
                                constrained_output=['project_directories']) as resources:
                stage_arguments = StageArguments(file_system=file_system, 
                                                 project_structure=self.project_structure, 
                                                 artifact_manifest=self.artifact_manifest, 
                                                 resources=resources)
                self.assertRaises(IllformedProjectError, setup_project, stage_arguments)
        except DeclaredResourceNotSuppliedError:
            pass

    def test_valid_project_with_hidden_file(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.project_directory,
                self.project_structure.main_resources_domain_root,
                self.project_structure.main_sources_domain_root,
            }, 
            files={
                join(self.project_structure.main_sources_root, '.hidden'): b''
            },
            working_directory=self.project_structure.project_directory
        )

        with StageResources(stage='setup_project', 
                            activation=0, 
                            resources={}, 
                            constrained_output=['project_directories']) as resources:
            stage_arguments = StageArguments(file_system=file_system, 
                                             project_structure=self.project_structure, 
                                             artifact_manifest=self.artifact_manifest, 
                                             resources=resources)
            setup_project(stage_arguments)

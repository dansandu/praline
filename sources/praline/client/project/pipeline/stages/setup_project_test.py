from praline.client.project.pipeline.stage_resources import DeclaredResourceNotSuppliedError, StageResources
from praline.client.project.pipeline.stages.setup_project import setup_project, IllformedProjectError
from praline.client.project.pipeline.stages import StageArguments
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform)
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class SetupProjectStageTest(TestCase):
    def setUp(self):
        self.artifact_manifest = ArtifactManifest(organization='my_organization',
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
        
        self.resources_full = join('project', 'resources', 'my_organization', 'my_artifact')

        self.sources_full = join('project', 'sources', 'my_organization', 'my_artifact')

    def test_project_setup(self):
        file_system = FileSystemMock(
            directories={
                'project',
            },
            working_directory='project'
        )

        with StageResources(stage='setup_project', 
                            activation=0, 
                            resources={}, 
                            constrained_output=['project_structure']) as resources:
            stage_arguments = StageArguments(file_system=file_system, 
                                             artifact_manifest=self.artifact_manifest, 
                                             resources=resources)
            setup_project(stage_arguments)

        self.assertEqual(resources['project_structure'], project_structure_dummy)

        self.assertTrue(file_system.is_directory(self.resources_full))

        self.assertTrue(file_system.is_directory(self.sources_full))

        for path in vars(project_structure_dummy).values():
            self.assertTrue(file_system.is_directory(path))

    def test_invalid_project_resources(self):        
        file_system = FileSystemMock(
            directories={
                self.resources_full,
                self.sources_full,
            },
            files={
                join('project', 'resources', 'my_organization', 'somefile'): b''
            },
            working_directory='project'
        )

        try:
            with StageResources(stage='setup_project', 
                                activation=0, 
                                resources={}, 
                                constrained_output=['project_structure']) as resources:
                stage_arguments = StageArguments(file_system=file_system, 
                                                 artifact_manifest=self.artifact_manifest, 
                                                 resources=resources)
                self.assertRaises(IllformedProjectError, setup_project, stage_arguments)
        except DeclaredResourceNotSuppliedError:
            pass

    def test_invalid_project_sources(self):
        file_system = FileSystemMock(
            directories={
                self.resources_full,
                self.sources_full,
            }, 
            files={
                join('project', 'sources', 'somefile'): b''
            },
            working_directory='project'
        )

        try:
            with StageResources(stage='setup_project', 
                                activation=0, 
                                resources={}, 
                                constrained_output=['project_structure']) as resources:
                stage_arguments = StageArguments(file_system=file_system, 
                                                 artifact_manifest=self.artifact_manifest, 
                                                 resources=resources)
                self.assertRaises(IllformedProjectError, setup_project, stage_arguments)
        except DeclaredResourceNotSuppliedError:
            pass

    def test_valid_project_with_hidden_file(self):
        file_system = FileSystemMock(
            directories={
                self.resources_full,
                self.sources_full,
            },
            files={
                join('project', 'sources', '.hidden'): b'',
            },
            working_directory='project'
        )

        with StageResources(stage='setup_project', 
                            activation=0, 
                            resources={}, 
                            constrained_output=['project_structure']) as resources:
            stage_arguments = StageArguments(file_system=file_system, 
                                             artifact_manifest=self.artifact_manifest, 
                                             resources=resources)
            setup_project(stage_arguments)

from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.test import test
from praline.client.project.pipeline.stages import StageArguments
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform, ArtifactDependency,
                            DependencyScope, ServiceConfiguration)
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from os.path import join
from typing import Dict, List
from unittest import TestCase


class TestStageTest(TestCase):
    def test_test(self):
        project_structure = ProjectStructure('project', 'org', 'art')

        test_library = join(project_structure.libraries_root, 'org-art.dll')

        test_service_runner_executable = join(project_structure.external_executables_root, 'anotherorg-anotherart.exe')
        test_program_arguments = ['test', 'program', 'arguments']

        expected_env = {
            'PRALINE_PROGRESS_BAR_STAGE_INDEX': '1',
            'PRALINE_PROGRESS_BAR_STAGE_COUNT': '5',
        }

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
            test_service=ServiceConfiguration(
                executable_to_run='anotherorg-anotherart',
                library_to_load='testorg-testart',
                service_name='custom_service'
            ),
            dependencies=[
                ArtifactDependency(
                    organization='anotherorg',
                    artifact='anotherart',
                    version=ArtifactVersion.from_string('1.0.0'),
                    scope=DependencyScope.main)
            ]) 

        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            self.assertEqual(command, [test_service_runner_executable, test_library, 'custom_service'] + test_program_arguments)
            self.assertEqual(add_to_library_path, [project_structure.external_libraries_root])
            self.assertTrue(interactive)
            self.assertEqual(add_to_env, expected_env)
            return True

        file_system = FileSystemMock(
            directories={
                project_structure.executables_root,
                project_structure.libraries_root,
                project_structure.external_libraries_root,
                project_structure.external_executables_root
            }, 
            files={
                test_service_runner_executable: b'',
                test_library: b'',
            },
            on_execute=on_execute
        )

        program_arguments = {
            'byStage': {
                'arguments': test_program_arguments
            }
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, 
                                                        expected_resolution=0, 
                                                        stage_index=1, 
                                                        stage_count=5)

        with StageResources(stage='test', 
                            activation=0, 
                            resources={
                                'project_directories': True,
                                'test_library': test_library,
                                'external_executables': [test_service_runner_executable]
                            }, 
                            constrained_output=['tests_passed']) as resources:
            stage_arguments = StageArguments(
                file_system=file_system,
                project_structure=project_structure,
                resources=resources,
                program_arguments=program_arguments, 
                artifact_manifest=artifact_manifest,
                progress_bar_supplier=progress_bar_supplier
            )
            test(stage_arguments)

        self.assertEqual(resources['tests_passed'], 'success')
 
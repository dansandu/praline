from praline.client.project.pipeline.stages.main import main
from praline.client.project.pipeline.stages import StageArguments
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from typing import Dict, List
from unittest import TestCase


class MainStageTest(TestCase):
    def test_main(self):
        resources_root          = project_structure_dummy.resources_root
        executables_root        = project_structure_dummy.executables_root
        external_libraries_root = project_structure_dummy.external_libraries_root

        main_executable        = join(project_structure_dummy.executables_root, 'main.exe')
        main_program_arguments = ['main', 'program', 'arguments']

        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            self.assertEqual(command, [main_executable] + main_program_arguments)
            self.assertEqual(add_to_library_path, [external_libraries_root, resources_root])
            self.assertTrue(interactive)
            return True


        file_system = FileSystemMock(
            directories={
                resources_root,
                executables_root,
                external_libraries_root,
            }, 
            files={
                main_executable: b''
            },
            on_execute=on_execute
        )

        program_arguments = {
            'byStage': {
                'arguments': main_program_arguments
            }
        }

        resources = {
            'project_structure': project_structure_dummy,
            'main_executable': main_executable
        }

        stage_arguments = StageArguments(file_system=file_system, 
                                         program_arguments=program_arguments, 
                                         resources=resources)

        main(stage_arguments)

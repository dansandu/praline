from praline.client.project.pipeline.stages.main import main
from praline.common import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from typing import Dict, List
from unittest import TestCase


class MainStageTest(TestCase):
    def test_main(self):
        resources_root          = 'project/resources'
        executables_root        = 'project/target/executables'
        external_libraries_root = 'project/target/external/libraries'

        main_executable        = 'project/target/executables/main.exe'
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

        resources = {
            'project_structure': ProjectStructure(
                project_directory='project',
                resources_root=resources_root,
                sources_root='project/sources',
                target_root='project/target',
                objects_root='project/target/objects',
                executables_root=executables_root,
                libraries_root='project/target/libraries',
                libraries_interfaces_root='project/target/libraries_interfaces',
                symbols_tables_root='project/target/symbols_tables',
                external_root='project/target/external',
                external_packages_root='project/target/external/packages',
                external_headers_root='project/target/external/headers',
                external_executables_root='project/target/external/executables',
                external_libraries_root=external_libraries_root,
                external_libraries_interfaces_root='project/target/external/libraries_interfaces',
                external_symbols_tables_root='project/target/external/symbols_tables'
            ),
            'main_executable': main_executable
        }

        program_arguments = {
            'byStage': {
                'arguments': main_program_arguments
            }
        }


        main(file_system, resources, None, program_arguments, None, None, None)

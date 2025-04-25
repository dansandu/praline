from praline.common.progress_bar import ProgressBarSupplier
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.link_main_executable import link_main_executable
from praline.common.project_structure import get_project_structure

from os.path import join
from typing import Any, Dict, List, Tuple
from unittest import TestCase


class CompilerMock:
    def __init__(self, test_case: TestCase, expected_objects: List[str], external_libraries: List[str], external_libraries_interfaces: List[str]):
        self.test_case                     = test_case
        self.expected_objects              = expected_objects
        self.external_libraries            = external_libraries
        self.external_libraries_interfaces = external_libraries_interfaces

    def link_executable_using_cache(self,
                                    objects: List[str],
                                    external_libraries: List[str],
                                    external_libraries_interfaces: List[str],
                                    cache: Dict[str, Any],
                                    progress_bar_supplier: ProgressBarSupplier,
                                    main_executable: bool) -> Tuple[str, str]:
        self.test_case.assertTrue(main_executable)
        self.test_case.assertCountEqual(objects, self.expected_objects)
        self.test_case.assertCountEqual(external_libraries, self.external_libraries)
        self.test_case.assertCountEqual(external_libraries_interfaces, self.external_libraries_interfaces)
        return ('theorg-theart-arm-linux-gcc-debug-0.0.0.exe', 'theorg-theart-arm-linux-gcc-debug-0.0.0.pdb')


class LinkMainExecutableStageTest(TestCase):
    def test_link_main_executable_without_main_library(self):
        project_structure = get_project_structure('project', 'theorg', 'theart')

        main_object_path = lambda object: join(project_structure.main_objects_root, object)
        
        external_library_path = lambda external_library: join(project_structure.external_libraries_root, external_library)

        external_interface_path = lambda external_interface: join(project_structure.external_libraries_interfaces_root, external_interface)

        object_x = main_object_path('theorg-theart-executable.obj')

        external_library = external_library_path('theorg-theart-arm-linux-gcc-debug.0.0.1.dll')
        
        external_library_interface = external_interface_path('otherorg-otherart-arm-linux-gcc-debug.0.0.2.lib')

        compiler = CompilerMock(
            self,
            expected_objects=[
                object_x,
            ],
            external_libraries=[
                external_library,
            ],
            external_libraries_interfaces=[
                external_library_interface,
            ]
        )

        with StageResources(
            stage='link_main_executable',
            activation=1,
            resources={
                'project_directories': True,
                'main_executable_object': object_x,
                'external_libraries': [
                    external_library,
                ],
                'external_libraries_interfaces': [
                    external_library_interface,
                ]
            },
            constrained_output=['main_executable', 'main_executable_symbols_table']
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            link_main_executable(stage_arguments)

        self.assertEqual(resources['main_executable'], 'theorg-theart-arm-linux-gcc-debug-0.0.0.exe')

        self.assertEqual(resources['main_executable_symbols_table'], 'theorg-theart-arm-linux-gcc-debug-0.0.0.pdb')

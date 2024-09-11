from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.link_main_library import link_main_library
from praline.common.project_structure import get_project_structure

from os.path import join
from typing import Any, Dict, List, Tuple
from unittest import TestCase


class CompilerMock:
    def __init__(self, 
                 test_case: TestCase,
                 expected_objects: List[str],
                 external_libraries: List[str],
                 external_libraries_interfaces: List[str]):
        self.test_case                     = test_case
        self.expected_objects              = expected_objects
        self.external_libraries            = external_libraries
        self.external_libraries_interfaces = external_libraries_interfaces

    def link_library_using_cache(self,
                                 objects: List[str],
                                 external_libraries: List[str],
                                 external_libraries_interfaces: List[str],
                                 cache: Dict[str, Any]) -> Tuple[str, str]:
        self.test_case.assertCountEqual(objects, self.expected_objects)
        self.test_case.assertCountEqual(external_libraries, self.external_libraries)
        self.test_case.assertCountEqual(external_libraries_interfaces, self.external_libraries_interfaces)
        return ('org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.dll', 
                'org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.lib', 
                'org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.pdb')


class LinkMainLibraryStageTest(TestCase):
    def setUp(self):
        self.project_structure = get_project_structure('project', 'org', 'art')

        self.source_path = lambda source: join(self.project_structure.sources_domain_root, source)

        self.external_header_path = lambda header: join(self.project_structure.external_headers_root, header)

        self.object_path = lambda object: join(self.project_structure.objects_root, object)
        
        self.external_library_path = lambda external_library: join(self.project_structure.external_libraries_root, external_library)

        self.external_interface_path = lambda external_interface: join(self.project_structure.external_libraries_interfaces_root, external_interface)

    def test_link_main_library(self):
        object_a = self.object_path('org-art-a.obj')
        object_b = self.object_path('org-art-b.obj')

        external_library = self.external_library_path('otherorg-otherart-arm-linux-gcc-debug.0.0.1.dll')
        
        external_library_interface = self.external_interface_path('otherorg-otherart-b-arm-linux-gcc-debug.0.0.2.lib')

        compiler = CompilerMock(
            self,
            expected_objects=[
                object_a,
                object_b,
            ],
            external_libraries=[
                external_library,
            ],
            external_libraries_interfaces=[
                external_library_interface,
            ]
        )

        with StageResources(
            stage='link_main_library',
            activation=0,
            resources={
                'project_directories': True,
                'main_objects': [
                    object_a,
                    object_b,
                ],
                'external_libraries': [
                    external_library,
                ],
                'external_libraries_interfaces': [
                    external_library_interface,
                ]
            },
            constrained_output=[
                'main_library', 
                'main_library_interface', 
                'main_library_symbols_table'
            ]
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            link_main_library(stage_arguments)

        self.assertEqual(resources['main_library'], 'org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.dll')

        self.assertEqual(resources['main_library_interface'], 'org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.lib')

        self.assertEqual(resources['main_library_symbols_table'], 'org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.pdb')

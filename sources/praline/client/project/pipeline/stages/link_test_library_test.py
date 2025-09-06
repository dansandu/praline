from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.link_test_library import link_test_library
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform)
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.project_structure import ProjectStructure

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
                                 cache: Dict[str, Any],
                                 progress_bar_supplier: ProgressBarSupplier,
                                 test_library: bool = False) -> Tuple[str, str]:
        self.test_case.assertTrue(test_library)
        self.test_case.assertCountEqual(objects, self.expected_objects)
        self.test_case.assertCountEqual(external_libraries, self.external_libraries)
        self.test_case.assertCountEqual(external_libraries_interfaces, self.external_libraries_interfaces)
        return ('org-art-arm-linux-gcc-debug-1.3.0.test.dll', 
                'org-art-arm-linux-gcc-debug-1.3.0.test.lib', 
                'org-art-arm-linux-gcc-debug-1.3.0.test.pdb')


class LinkTestLibraryStageTest(TestCase):
    def test_link_test_library(self):
        project_structure = ProjectStructure('project', 'org', 'art')

        main_object_path = lambda object: join(project_structure.main_objects_root, object)

        test_object_path = lambda object: join(project_structure.test_objects_root, object)
        
        external_library_path = lambda external_library: join(project_structure.external_libraries_root, external_library)

        external_interface_path = lambda external_interface: join(project_structure.external_libraries_interfaces_root, external_interface)

        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('1.3.0'),
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

        object_a = main_object_path('org-art-a.obj')
        object_b = main_object_path('org-art-b.obj')

        object_d = test_object_path('org-art-c.test.obj')
        object_e = test_object_path('org-art-d.test.obj')

        external_library = external_library_path('org-art-a-arm-linux-gcc-debug.0.0.1.dll')
        
        external_library_interface = external_interface_path('org-art-b-arm-linux-gcc-debug.0.0.2.lib')

        compiler = CompilerMock(self,
                                expected_objects=[
                                    object_a,
                                    object_b,
                                    object_d,
                                    object_e,
                                ],
                                external_libraries=[
                                    external_library,
                                ],
                                external_libraries_interfaces=[
                                    external_library_interface,
                                ])

        with StageResources(
            stage='link_main_library',
            activation=0,
            resources={
                'project_directories': True,
                'main_objects': [
                    object_a,
                    object_b,
                ],
                'test_objects': [
                    object_d,
                    object_e,
                ],
                'external_libraries': [
                    external_library,
                ],
                'external_libraries_interfaces': [
                    external_library_interface,
                ]
            },
            constrained_output=[
                'test_library', 
                'test_library_interface',
                'test_library_symbols_table',
            ]
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, artifact_manifest=artifact_manifest, resources=resources)
            link_test_library(stage_arguments)

        self.assertEqual(resources['test_library'], 'org-art-arm-linux-gcc-debug-1.3.0.test.dll')

        self.assertEqual(resources['test_library_interface'], 'org-art-arm-linux-gcc-debug-1.3.0.test.lib')

        self.assertEqual(resources['test_library_symbols_table'], 'org-art-arm-linux-gcc-debug-1.3.0.test.pdb')

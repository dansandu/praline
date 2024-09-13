from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.link_test_executable import link_test_executable
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform)
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

    def link_executable_using_cache(self,
                                    objects: List[str],
                                    external_libraries: List[str],
                                    external_libraries_interfaces: List[str],
                                    cache: Dict[str, Any],
                                    main_executable: bool) -> Tuple[str, str]:
        self.test_case.assertFalse(main_executable)
        self.test_case.assertCountEqual(objects, self.expected_objects)
        self.test_case.assertCountEqual(external_libraries, self.external_libraries)
        self.test_case.assertCountEqual(external_libraries_interfaces, self.external_libraries_interfaces)
        return ('org-art-arm-linux-gcc-debug-1.3.0.test.exe', 'org-art-arm-linux-gcc-debug-1.3.0.test.pdb')


class LinkTestExecutableStageTest(TestCase):
    def test_link_test_executable(self):
        project_structure = get_project_structure('project', 'org', 'art')

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
            dependencies=[]
        )

        object_a = main_object_path('org-art-a.obj')
        object_b = main_object_path('org-art-b.obj')
        object_c = main_object_path('org-art-executable.obj')

        object_d = test_object_path('org-art-c.test.obj')
        object_e = test_object_path('org-art-d.test.obj')
        object_f = test_object_path('org-art-executable.test.obj')

        external_library = external_library_path('org-art-a-arm-linux-gcc-debug.0.0.1.dll')
        
        external_library_interface = external_interface_path('org-art-b-arm-linux-gcc-debug.0.0.2.lib')

        compiler = CompilerMock(self,
                                expected_objects=[
                                    object_a,
                                    object_b,
                                    object_d,
                                    object_e,
                                    object_f,
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
                    object_c,
                ],
                'test_objects': [
                    object_d,
                    object_e,
                    object_f,
                ],
                'external_libraries': [
                    external_library,
                ],
                'external_libraries_interfaces': [
                    external_library_interface,
                ]
            },
            constrained_output=[
                'test_executable', 
                'test_executable_symbols_table',
            ]
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, artifact_manifest=artifact_manifest, resources=resources)
            link_test_executable(stage_arguments)

        self.assertEqual(resources['test_executable'], 'org-art-arm-linux-gcc-debug-1.3.0.test.exe')

        self.assertEqual(resources['test_executable_symbols_table'], 'org-art-arm-linux-gcc-debug-1.3.0.test.pdb')

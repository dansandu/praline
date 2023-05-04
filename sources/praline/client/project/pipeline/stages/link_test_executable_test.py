from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import StageArguments
from praline.client.project.pipeline.stages.link_test_executable import link_test_executable
from praline.common import (Architecture, ArtifactLoggingLevel, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            Compiler, ExportedSymbols, Mode, Platform, ProjectStructure)
from praline.common.testing import project_structure_dummy

from os.path import join
from typing import Any, Dict, List, Tuple
from unittest import TestCase


class CompilerWrapperMock:
    def __init__(self, 
                 test_case: TestCase,
                 expected_artifact_identifier: str,
                 expected_objects: List[str],
                 external_libraries: List[str],
                 external_libraries_interfaces: List[str]):
        self.test_case                     = test_case
        self.expected_artifact_identifier  = expected_artifact_identifier
        self.expected_objects              = expected_objects
        self.external_libraries            = external_libraries
        self.external_libraries_interfaces = external_libraries_interfaces

    def link_executable_using_cache(self,
                                    project_structure: ProjectStructure,
                                    artifact_identifier: str,
                                    objects: List[str],
                                    external_libraries: List[str],
                                    external_libraries_interfaces: List[str],
                                    cache: Dict[str, Any]) -> Tuple[str, str]:
        self.test_case.assertEqual(artifact_identifier, self.expected_artifact_identifier)
        self.test_case.assertCountEqual(objects, self.expected_objects)
        self.test_case.assertCountEqual(external_libraries, self.external_libraries)
        self.test_case.assertCountEqual(external_libraries_interfaces, self.external_libraries_interfaces)
        return ('org-art-arm-linux-gcc-debug-1.3.0.test.exe', 
                'org-art-arm-linux-gcc-debug-1.3.0.test.pdb')


class LinkTestExecutableStageTest(TestCase):
    def test_link_test_executable(self):
        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('1.3.0'),
            mode=Mode.debug,
            architecture=Architecture.arm,
            platform=Platform.linux,
            compiler=Compiler.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.library,
            artifact_logging_level=ArtifactLoggingLevel.debug,
            dependencies=[]
        )

        object_a = join(project_structure_dummy.objects_root, 'org-art-a.obj')
        object_b = join(project_structure_dummy.objects_root, 'org-art-b.obj')
        object_c = join(project_structure_dummy.objects_root, 'org-art-executable.obj')
        object_d = join(project_structure_dummy.objects_root, 'org-art-c.test.obj')
        object_e = join(project_structure_dummy.objects_root, 'org-art-d.test.obj')
        object_f = join(project_structure_dummy.objects_root, 'org-art-executable.test.obj')


        external_library = join(project_structure_dummy.external_libraries_root, 
                                'org-art-a-arm-linux-gcc-debug.0.0.1.dll')
        
        external_library_interface = join(project_structure_dummy.external_libraries_interfaces_root, 
                                          'org-art-b-arm-linux-gcc-debug.0.0.2.lib')

        compiler = CompilerWrapperMock(self,
                                       expected_artifact_identifier='org-art-arm-linux-gcc-debug-1.3.0.test',
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

        resources = StageResources(
            stage='link_main_library',
            activation=0,
            resources={
                'project_structure': project_structure_dummy,
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
                'main_executable_object': object_c,
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
        )

        stage_arguments = StageArguments(artifact_manifest=artifact_manifest,
                                         compiler=compiler,
                                         resources=resources)
        
        link_test_executable(stage_arguments)

        self.assertEqual(resources['test_executable'], 'org-art-arm-linux-gcc-debug-1.3.0.test.exe')

        self.assertEqual(resources['test_executable_symbols_table'], 'org-art-arm-linux-gcc-debug-1.3.0.test.pdb')

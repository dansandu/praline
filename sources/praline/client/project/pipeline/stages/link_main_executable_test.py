from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.link_main_executable import link_main_executable
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
        return ('org-art-arm-linux-gcc-debug-0.0.0.exe', 'org-art-arm-linux-gcc-debug-0.0.0.pdb')


class LinkMainExecutableStageTest(TestCase):
    def test_link_main_executable(self):
        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('0.0.0'),
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

        external_library = join(project_structure_dummy.external_libraries_root, 
                                'org-art-a-arm-linux-gcc-debug.0.0.1.dll')
        
        external_library_interface = join(project_structure_dummy.external_libraries_interfaces_root, 
                                          'org-art-b-arm-linux-gcc-debug.0.0.2.lib')

        compiler = CompilerWrapperMock(self,
                                       expected_artifact_identifier='org-art-arm-linux-gcc-debug-0.0.0',
                                       expected_objects=[
                                           object_a,
                                           object_b,
                                       ],
                                       external_libraries=[
                                           external_library,
                                       ],
                                       external_libraries_interfaces=[
                                           external_library_interface,
                                       ])

        resources = StageResources(
            stage='link_main_executable',
            activation=0,
            resources={
                'project_structure': project_structure_dummy,
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
            constrained_output=['main_executable', 'main_executable_symbols_table']
        )

        stage_arguments = StageArguments(artifact_manifest=artifact_manifest,
                                         compiler=compiler,
                                         resources=resources)
        
        link_main_executable(stage_arguments)

        self.assertEqual(resources['main_executable'], 'org-art-arm-linux-gcc-debug-0.0.0.exe')

        self.assertEqual(resources['main_executable_symbols_table'], 'org-art-arm-linux-gcc-debug-0.0.0.pdb')

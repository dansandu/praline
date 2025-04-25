from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.link_main_library import link_main_library, predicate
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform)
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.project_structure import get_project_structure
from praline.common.testing.file_system_mock import FileSystemMock

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
        self.test_case.assertFalse(test_library)
        self.test_case.assertCountEqual(objects, self.expected_objects)
        self.test_case.assertCountEqual(external_libraries, self.external_libraries)
        self.test_case.assertCountEqual(external_libraries_interfaces, self.external_libraries_interfaces)
        return ('org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.dll', 
                'org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.lib', 
                'org-art-arm-linux-gcc-debug-0.5.0.SNAPSHOT.pdb')


class LinkMainLibraryStageTest(TestCase):        
    def test_link_main_library(self):
        project_structure = get_project_structure('project', 'org', 'art')

        main_source_path = lambda source: join(project_structure.main_sources_domain_root, source)

        main_object_path = lambda object: join(project_structure.main_objects_root, object)

        external_library_path = lambda external_library: join(project_structure.external_libraries_root, external_library)

        external_interface_path = lambda external_interface: join(project_structure.external_libraries_interfaces_root, external_interface)

        source_a = main_source_path('a.cpp')
        source_b = main_source_path('b.cpp')

        object_a = main_object_path('org-art-a.obj')
        object_b = main_object_path('org-art-b.obj')

        external_library = external_library_path('otherorg-otherart-arm-linux-gcc-debug.0.0.1.dll')
        
        external_library_interface = external_interface_path('otherorg-otherart-b-arm-linux-gcc-debug.0.0.2.lib')

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

        file_system = FileSystemMock(
            directories={
                project_structure.main_sources_domain_root,
                project_structure.main_objects_root,
                project_structure.external_libraries_root,
                project_structure.external_libraries_interfaces_root,
            },
            files={
                source_a: b'',
                source_b: b'',
                object_a: b'',
                object_b: b'',
            }
        )

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
            test_service_runner=None,
            test_service_name='default',
            dependencies=[]
        )

        predicate_result = predicate(StageArguments(project_structure=project_structure, file_system=file_system, artifact_manifest=artifact_manifest))

        self.assertTrue(predicate_result.can_run)

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

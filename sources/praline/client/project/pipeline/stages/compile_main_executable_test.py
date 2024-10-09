from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.compile_main_executable import compile_main_executable
from praline.common.project_structure import get_project_structure
from praline.common.progress_bar import ProgressBarSupplier

from os.path import join
from unittest import TestCase
from typing import Any, Dict, List


class CompilerMock:
    def __init__(self, test_case: TestCase, expected_headers, sources_to_objects: Dict[str, str]):
        self.test_case          = test_case
        self.expected_headers   = expected_headers
        self.sources_to_objects = sources_to_objects

    def compile_sources_using_cache(self,
                                    headers: List[str],
                                    sources: List[str],
                                    cache: Dict[str, Any],
                                    progress_bar_supplier: ProgressBarSupplier,
                                    main_sources: bool) -> List[str]:
        self.test_case.assertTrue(main_sources)
        self.test_case.assertCountEqual(headers, self.expected_headers)
        return [self.sources_to_objects[source] for source in sources]


class CompileMainExecutableSourceStageTest(TestCase):
    def setUp(self):
        self.project_structure = get_project_structure('project', 'org', 'art')

        self.main_source_path = lambda source: join(self.project_structure.main_sources_domain_root, source)

        self.external_header_path = lambda header: join(self.project_structure.external_headers_root, header)

        self.main_object_path = lambda object: join(self.project_structure.main_objects_root, object)

    def test_with_formatted_sources(self):
        header_a = self.main_source_path('a.hpp')
        header_b = self.main_source_path('b.hpp')
        
        source_executable = self.main_source_path('executable.cpp')

        object_executable = self.main_object_path('org-art-executable.obj')

        header_c = self.external_header_path('c.hpp')

        compiler = CompilerMock(
            self,
            expected_headers=[
                header_a,
                header_b,
                header_c,
            ],
            sources_to_objects={
                source_executable: object_executable,
            }
        )

        with StageResources(
            stage='compile_main_executable',
            activation=0,
            resources={
                'project_directories': True,
                'formatted_main_headers': [
                    header_a,
                    header_b,
                ],
                'formatted_main_executable_source': source_executable,
                'external_headers': [
                    header_c,
                ]
            },
            constrained_output=['main_executable_object']
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            compile_main_executable(stage_arguments)

        self.assertCountEqual(resources['main_executable_object'], object_executable)

    def test_with_unformatted_sources(self):
        header_a = self.main_source_path('a.hpp')
        header_b = self.main_source_path('b.hpp')

        source_executable = self.main_source_path('executable.cpp')

        object_executable = self.main_object_path('org-art-executable.obj')

        header_c = self.external_header_path('c.hpp')

        compiler = CompilerMock(
            self,
            expected_headers=[
                header_a,
                header_b,
                header_c,
            ],
            sources_to_objects={
                source_executable: object_executable,
            }
        )

        with StageResources(
            stage='compile_main_executable',
            activation=1,
            resources={
                'project_directories': True,
                'main_headers': [
                    header_a,
                    header_b,
                ],
                'main_executable_source': source_executable,
                'external_headers': [
                    header_c,
                ]
            },
            constrained_output=['main_executable_object']
        ) as resources:            
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            compile_main_executable(stage_arguments)

        self.assertCountEqual(resources['main_executable_object'], object_executable)

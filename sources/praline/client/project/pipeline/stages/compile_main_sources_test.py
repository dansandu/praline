from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.compile_main_sources import compile_main_sources
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.project_structure import ProjectStructure

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


class CompileMainSourcesStageTest(TestCase):
    def setUp(self):
        self.project_structure = ProjectStructure('project', 'someorg', 'someart')

        self.main_generated_source_path = lambda source: join(self.project_structure.main_generated_sources_root, source)

        self.main_source_path = lambda source: join(self.project_structure.main_sources_domain_root, source)

        self.main_object_path = lambda object: join(self.project_structure.main_objects_root, object)
        
        self.external_header_path = lambda header: join(self.project_structure.external_headers_root, header)

    def test_with_generated_sources(self):

        header_a = self.main_source_path('a.hpp')
        source_a = self.main_source_path('a.cpp')
        object_a = self.main_object_path('org-art-a.obj')

        header_b = self.main_source_path('b.hpp')
        source_b = self.main_source_path('b.cpp')
        object_b = self.main_object_path('org-art-b.obj')

        header_c = self.external_header_path('c.hpp')

        header_d = self.main_generated_source_path('d.hpp')
        source_d = self.main_generated_source_path('d.cpp')
        object_d = self.main_object_path('theorg-theart-d.obj')

        compiler = CompilerMock(
            self,
            expected_headers=[
                header_d,
                header_a,
                header_b,
                header_c,
            ],
            sources_to_objects={
                source_a: object_a,
                source_b: object_b,
                source_d: object_d,
            }
        )

        with StageResources(
            stage='compile_main_sources',
            resources={
                'main_headers': [
                    header_a,
                    header_b,
                ],
                'main_sources': [
                    source_a,
                    source_b,
                ],
                'external_headers': [
                    header_c,
                ],
                'main_farseer_cpp_headers': [
                    header_d,
                ],
                'main_farseer_cpp_sources': [
                    source_d,
                ],
            },
            constrained_output=['main_objects']
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            compile_main_sources(stage_arguments)

        expected_objects = {
            object_a,
            object_b,
            object_d,
        }

        self.assertCountEqual(resources['main_objects'], expected_objects)

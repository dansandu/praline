from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.compile_test_sources import compile_test_sources
from praline.common.project_structure import get_project_structure
from praline.common.progress_bar import ProgressBarSupplier

from os.path import join
from typing import Any, Dict, List
from unittest import TestCase


class CompilerMock:
    def __init__(self, test_case: TestCase, expected_headers, sources_to_objects: Dict[str, str]):
        self.test_case          = test_case
        self.expected_headers   = expected_headers
        self.sources_to_objects = sources_to_objects

    def compile_using_cache(self,
                            headers: List[str],
                            sources: List[str],
                            cache: Dict[str, Any],
                            progress_bar_supplier: ProgressBarSupplier) -> List[str]:
        self.test_case.assertEqual(set(headers), set(self.expected_headers))
        return [self.sources_to_objects[source] for source in sources]


class CompileTestSourcesStageTest(TestCase):
    def setUp(self):
        self.project_structure = get_project_structure('project', 'theorg', 'theart')

        self.source_path = lambda source: join(self.project_structure.sources_domain_root, source)

        self.external_header_path = lambda header: join(self.project_structure.external_headers_root, header)

        self.object_path = lambda object: join(self.project_structure.objects_root, object)

    def test_with_formatted_sources(self):
        header_a = self.source_path('a.hpp')
        source_a = self.source_path('a.test.cpp')
        object_a = self.object_path('theorg-theart-a.test.obj')

        header_b = self.source_path('b.hpp')
        source_b = self.source_path('b.test.cpp')
        object_b = self.object_path('theorg-theart-b.test.obj')

        header_c = self.external_header_path('c.hpp')

        compiler = CompilerMock(
            self,
            expected_headers=[
                header_a,
                header_b,
                header_c,
            ],
            sources_to_objects={
                source_a: object_a,
                source_b: object_b,
            }
        )

        with StageResources(
            stage='compile_test_sources',
            activation=0,
            resources={
                'formatted_headers': [
                    header_a,
                    header_b,
                ],
                'formatted_test_sources': [
                    source_a,
                    source_b,
                ],
                'external_headers': [
                    header_c,
                ]
            },
            constrained_output=['test_objects']
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            compile_test_sources(stage_arguments)

        expected_objects = {
            object_a,
            object_b,
        }

        self.assertEqual(set(resources['test_objects']), expected_objects)

    def test_without_formatted_sources(self):
        header_a = self.source_path('a.hpp')
        source_a = self.source_path('a.test.cpp')
        object_a = self.object_path('org-art-a.test.obj')

        header_b = self.source_path('b.hpp')
        source_b = self.source_path('b.test.cpp')
        object_b = self.object_path('org-art-b.test.obj')

        header_c = self.external_header_path('c.hpp')

        compiler = CompilerMock(
            self,
            expected_headers=[
                header_a,
                header_b,
                header_c,
            ],
            sources_to_objects={
                source_a: object_a,
                source_b: object_b,
            }
        )

        with StageResources(
            stage='compile_test_sources',
            activation=1,
            resources={
                'headers': [
                    header_a,
                    header_b,
                ],
                'test_sources': [
                    source_a,
                    source_b,
                ],
                'external_headers': [
                    header_c,
                ]
            },
            constrained_output=['test_objects']
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            compile_test_sources(stage_arguments)

        expected_objects = {
            object_a,
            object_b,
        }

        self.assertCountEqual(resources['test_objects'], expected_objects)

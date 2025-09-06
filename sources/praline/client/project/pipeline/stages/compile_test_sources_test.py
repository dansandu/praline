from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.compile_test_sources import compile_test_sources
from praline.common.project_structure import ProjectStructure
from praline.common.progress_bar import ProgressBarSupplier

from os.path import join
from typing import Any, Dict, List
from unittest import TestCase


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
        self.test_case.assertFalse(main_sources)
        self.test_case.assertEqual(set(headers), set(self.expected_headers))
        return [self.sources_to_objects[source] for source in sources]


class CompileTestSourcesStageTest(TestCase):
    def setUp(self):
        self.project_structure = ProjectStructure('project', 'theorg', 'theart')

        self.main_generated_source_path = lambda source: join(self.project_structure.main_generated_sources_root, source)
        
        self.test_generated_source_path = lambda source: join(self.project_structure.test_generated_sources_root, source)

        self.main_source_path = lambda source: join(self.project_structure.main_sources_domain_root, source)

        self.test_source_path = lambda source: join(self.project_structure.test_sources_domain_root, source)

        self.external_header_path = lambda header: join(self.project_structure.external_headers_root, header)

        self.main_object_path = lambda object: join(self.project_structure.main_objects_root, object)

        self.test_object_path = lambda object: join(self.project_structure.test_objects_root, object)

    def test_with_formatted_sources(self):
        main_header_farseer_a = self.main_generated_source_path('farseer_a.hpp')

        test_header_farseer_b = self.test_generated_source_path('farseer_b.hpp')
        test_source_farseer_b = self.test_generated_source_path('farseer_b.cpp')
        test_object_farseer_b = self.main_object_path('theorg-theart-farseer_b.obj')

        main_header_a = self.main_source_path('a.hpp')
        main_source_a = self.main_source_path('a.cpp')
        main_object_a = self.main_object_path('theorg-theart-a.obj')

        test_header_a = self.test_source_path('a.test.hpp')
        test_source_a = self.test_source_path('a.test.cpp')
        test_object_a = self.test_object_path('theorg-theart-a.test.obj')

        test_header_b = self.test_source_path('b.test.hpp')
        test_source_b = self.test_source_path('b.test.cpp')
        test_object_b = self.test_object_path('theorg-theart-b.test.obj')

        external_header_c = self.external_header_path('c.hpp')

        compiler = CompilerMock(
            self,
            expected_headers=[
                main_header_farseer_a,
                test_header_farseer_b,
                main_header_a,
                test_header_a,
                test_header_b,
                external_header_c,
            ],
            sources_to_objects={
                main_source_a: main_object_a,
                test_source_farseer_b: test_object_farseer_b,
                test_source_a: test_object_a,
                test_source_b: test_object_b,
            }
        )

        with StageResources(
            stage='compile_test_sources',
            activation=0,
            resources={
                'generated_main_farseer_cpp_headers': [
                    main_header_farseer_a,
                ],
                'generated_test_farseer_cpp_headers': [
                    test_header_farseer_b,
                ],
                'generated_test_farseer_cpp_sources': [
                    test_source_farseer_b,
                ],
                'formatted_main_headers': [
                    main_header_a,
                ],
                'formatted_test_headers': [
                    test_header_a,
                    test_header_b,
                ],
                'formatted_test_sources': [
                    test_source_a,
                    test_source_b,
                ],
                'external_headers': [
                    external_header_c,
                ]
            },
            constrained_output=['test_objects']
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            compile_test_sources(stage_arguments)

        expected_objects = {
            test_object_farseer_b,
            test_object_a,
            test_object_b,
        }

        self.assertEqual(set(resources['test_objects']), expected_objects)

    def test_without_formatted_sources(self):
        main_header_farseer_a = self.main_generated_source_path('farseer_a.hpp')
        main_object_farseer_a = self.main_object_path('theorg-theart-farseer_a.obj')

        test_header_farseer_b = self.test_generated_source_path('farseer_b.hpp')
        test_source_farseer_b = self.test_generated_source_path('farseer_b.cpp')
        test_object_farseer_b = self.main_object_path('theorg-theart-farseer_b.obj')

        main_header_a = self.main_source_path('a.hpp')
        main_source_a = self.main_source_path('a.cpp')
        main_object_a = self.main_object_path('theorg-theart-a.obj')

        test_header_a = self.test_source_path('a.test.hpp')
        test_source_a = self.test_source_path('a.test.cpp')
        test_object_a = self.test_object_path('theorg-theart-a.test.obj')

        test_header_b = self.test_source_path('b.test.hpp')
        test_source_b = self.test_source_path('b.test.cpp')
        test_object_b = self.test_object_path('theorg-theart-b.test.obj')

        external_header_c = self.external_header_path('c.hpp')

        compiler = CompilerMock(
            self,
            expected_headers=[
                main_header_farseer_a,
                test_header_farseer_b,
                main_header_a,
                test_header_a,
                test_header_b,
                external_header_c,
            ],
            sources_to_objects={
                main_source_a: main_object_a,
                test_source_farseer_b: test_object_farseer_b,
                test_source_a: test_object_a,
                test_source_b: test_object_b,
            }
        )

        with StageResources(
            stage='compile_test_sources',
            activation=1,
            resources={
                'generated_main_farseer_cpp_headers': [
                    main_header_farseer_a,
                ],
                'generated_test_farseer_cpp_headers': [
                    test_header_farseer_b,
                ],
                'generated_test_farseer_cpp_sources': [
                    test_source_farseer_b,
                ],
                'main_headers': [
                    main_header_a,
                ],
                'test_headers': [
                    test_header_a,
                    test_header_b,
                ],
                'test_sources': [
                    test_source_a,
                    test_source_b,
                ],
                'external_headers': [
                    external_header_c,
                ]
            },
            constrained_output=['test_objects']
        ) as resources:
            stage_arguments = StageArguments(compiler=compiler, resources=resources)
            compile_test_sources(stage_arguments)

        expected_objects = {
            test_object_farseer_b,
            test_object_a,
            test_object_b,
        }

        self.assertEqual(set(resources['test_objects']), expected_objects)

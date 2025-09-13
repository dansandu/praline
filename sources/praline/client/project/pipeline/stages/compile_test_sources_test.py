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

    def test_with_generated_sources(self):
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

        main_header_d = self.main_generated_source_path('d.hpp')
        main_source_d = self.main_generated_source_path('d.cpp')
        main_object_d = self.main_object_path('theorg-theart-d.obj')

        test_header_e = self.test_generated_source_path('e.hpp')
        test_source_e = self.test_generated_source_path('e.cpp')
        test_object_e = self.test_object_path('theorg-theart-e.obj')

        compiler = CompilerMock(
            self,
            expected_headers=[
                main_header_a,
                test_header_a,
                test_header_b,
                external_header_c,
                main_header_d,
                test_header_e,
            ],
            sources_to_objects={
                main_source_a: main_object_a,
                test_source_a: test_object_a,
                test_source_b: test_object_b,
                main_source_d: main_object_d,
                test_source_e: test_object_e,
            }
        )

        with StageResources(
            stage='compile_test_sources',
            resources={
                'main_farseer_cpp_headers': [
                    main_header_d,
                ],
                'main_headers': [
                    main_header_a,
                ],
                'test_farseer_cpp_headers': [
                    test_header_e,
                ],
                'test_farseer_cpp_sources': [
                    test_source_e,
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
            test_object_a,
            test_object_b,
            test_object_e,
        }

        self.assertEqual(set(resources['test_objects']), expected_objects)

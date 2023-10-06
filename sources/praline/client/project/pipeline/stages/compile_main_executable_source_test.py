from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.compile_main_executable_source import compile_main_executable_source
from praline.common import ProjectStructure
from praline.common.compiling.compiler import IYieldDescriptor
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.testing import project_structure_dummy

from os.path import join
from unittest import TestCase
from typing import Any, Dict, List


class YieldDescriptorMock:
    def __init__(self, sources_to_objects: Dict[str, str]):
        self.sources_to_objects = sources_to_objects

    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        return self.sources_to_objects[source]


class CompilerWrapperMock:
    def __init__(self, test_case: TestCase, expected_headers, sources_to_objects: Dict[str, str]):
        self.test_case          = test_case
        self.expected_headers   = expected_headers
        self.sources_to_objects = sources_to_objects
        self.yield_descriptor   = YieldDescriptorMock(sources_to_objects)

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return self.yield_descriptor

    def compile_using_cache(self,
                            project_structure: ProjectStructure,
                            headers: List[str],
                            sources: List[str],
                            cache: Dict[str, Any],
                            progress_bar_supplier: ProgressBarSupplier) -> List[str]:
        self.test_case.assertCountEqual(headers, self.expected_headers)
        return [self.sources_to_objects[source] for source in sources]


class CompileMainExecutableSourceStageTest(TestCase):
    def test_with_formatted_sources(self):
        header_a = join(project_structure_dummy.sources_root, 'org', 'art', 'a.hpp')
        header_b = join(project_structure_dummy.sources_root, 'org', 'art', 'b.hpp')
        header_c = join(project_structure_dummy.external_headers_root, 'org', 'art', 'c.hpp')

        source_executable = join(project_structure_dummy.sources_root, 'org', 'art', 'executable.cpp')
        object_executable = join(project_structure_dummy.objects_root, 'org-art-executable.obj')

        compiler = CompilerWrapperMock(
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
            stage='compile_main_executable_source',
            activation=0,
            resources={
                'project_structure': project_structure_dummy,
                'formatted_headers': [
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
            compile_main_executable_source(stage_arguments)

        self.assertCountEqual(resources['main_executable_object'], object_executable)


    def test_with_unformatted_sources(self):
        header_a = join(project_structure_dummy.sources_root, 'org', 'art', 'a.hpp')
        header_b = join(project_structure_dummy.sources_root, 'org', 'art', 'b.hpp')
        header_c = join(project_structure_dummy.external_headers_root, 'org', 'art', 'c.hpp')

        source_executable = join(project_structure_dummy.sources_root, 'org', 'art', 'executable.cpp')
        object_executable = join(project_structure_dummy.objects_root, 'org-art-executable.obj')

        compiler = CompilerWrapperMock(
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
            stage='compile_main_executable_source',
            activation=1,
            resources={
                'project_structure': project_structure_dummy,
                'headers': [
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
            compile_main_executable_source(stage_arguments)

        self.assertCountEqual(resources['main_executable_object'], object_executable)

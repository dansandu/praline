from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.compile_main_sources import compile_main_sources
from praline.common import ProjectStructure
from praline.common.compiling.compiler import IYieldDescriptor
from praline.common.progress_bar import ProgressBarSupplier

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
        self.test_case.assertEqual(set(headers), set(self.expected_headers))
        return [self.sources_to_objects[source] for source in sources]


class CompileMainSourcesStageTest(TestCase):
    def setUp(self):
        self.project_structure = ProjectStructure(
            project_directory='project',
            resources_root='project/resources',
            sources_root='project/sources',
            target_root='project/target',
            objects_root='project/target/objects',
            executables_root='project/target/executables',
            libraries_root='project/target/libraries',
            libraries_interfaces_root='project/target/libraries_interfaces',
            symbols_tables_root='project/target/symbols_tables',
            external_root='project/target/external',
            external_packages_root='project/target/external/packages',
            external_headers_root='project/target/external/headers',
            external_executables_root='project/target/external/executables',
            external_libraries_root='project/target/external/libraries',
            external_libraries_interfaces_root='project/target/external/libraries_interfaces',
            external_symbols_tables_root='project/target/external/symbols_tables'
        )

    def test_with_formatted_executable(self):
        resources = StageResources(
            stage='compile_main_sources',
            activation=0,
            resources={
                'project_structure': self.project_structure,
                'formatted_headers': [
                    'project/sources/org/art/a.hpp',
                    'project/sources/org/art/b.hpp',
                ],
                'formatted_main_sources': [
                    'project/sources/org/art/a.cpp',
                    'project/sources/org/art/b.cpp',
                    'project/sources/org/art/executable.cpp',
                ],
                'formatted_main_executable_source': 'project/sources/org/art/executable.cpp',
                'external_headers': [
                    'project/target/external/headers/org/art/c.hpp'
                ]
            },
            constrained_output=['main_objects', 'main_executable_object']
        )

        configuration = {
            'compiler': CompilerWrapperMock(
                self,
                expected_headers=[
                    'project/sources/org/art/a.hpp',
                    'project/sources/org/art/b.hpp',
                    'project/target/external/headers/org/art/c.hpp'
                ],
                sources_to_objects={
                    'project/sources/org/art/a.cpp': 'project/target/objects/org-art-a.obj',
                    'project/sources/org/art/b.cpp': 'project/target/objects/org-art-b.obj',
                    'project/sources/org/art/executable.cpp': 'project/target/objects/org-art-executable.obj',
                }
            )
        }
        
        compile_main_sources(None, resources, None, None, configuration, None, None)

        self.assertIn('main_objects', resources)

        expected_objects = {
            'project/target/objects/org-art-a.obj',
            'project/target/objects/org-art-b.obj',
            'project/target/objects/org-art-executable.obj',
        }

        self.assertEqual(set(resources['main_objects']), expected_objects)

        self.assertIn('main_executable_object', resources)

        self.assertEqual(resources['main_executable_object'], 'project/target/objects/org-art-executable.obj')

    def test_without_executable(self):
        resources = StageResources(
            stage='compile_main_sources',
            activation=1,
            resources={
                'project_structure': self.project_structure,
                'headers': [
                    'project/sources/org/art/a.hpp',
                    'project/sources/org/art/b.hpp',
                ],
                'main_sources': [
                    'project/sources/org/art/a.cpp',
                    'project/sources/org/art/b.cpp',
                ],
                'main_executable_source': None,
                'external_headers': [
                    'project/target/external/headers/org/art/c.hpp'
                ]
            },
            constrained_output=['main_objects', 'main_executable_object']
        )

        configuration = {
            'compiler': CompilerWrapperMock(
                self,
                expected_headers=[
                    'project/sources/org/art/a.hpp',
                    'project/sources/org/art/b.hpp',
                    'project/target/external/headers/org/art/c.hpp'
                ],
                sources_to_objects={
                    'project/sources/org/art/a.cpp': 'project/target/objects/org-art-a.obj',
                    'project/sources/org/art/b.cpp': 'project/target/objects/org-art-b.obj',
                }
            )
        }
        
        compile_main_sources(None, resources, None, None, configuration, None, None)

        self.assertIn('main_objects', resources)

        expected_objects = {
            'project/target/objects/org-art-a.obj',
            'project/target/objects/org-art-b.obj',
        }

        self.assertEqual(set(resources['main_objects']), expected_objects)

        self.assertIn('main_executable_object', resources)

        self.assertEqual(resources['main_executable_object'], None)
 
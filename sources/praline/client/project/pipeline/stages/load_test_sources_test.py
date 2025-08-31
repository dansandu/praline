from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_test_sources import load_test_sources, predicate
from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadTestSourcesStageTest(TestCase):
    def test_load_test_sources(self):        
        project_structure = ProjectStructure('project', 'org', 'art')

        main_source_path = lambda source: join(project_structure.main_sources_domain_root, source)

        test_source_path = lambda source: join(project_structure.test_sources_domain_root, source)
        
        main_header_math = main_source_path('math.hpp')
        main_source_math = main_source_path('math.cpp')

        test_source_math = test_source_path('math.test.cpp')
        test_source_lib  = test_source_path('lib.cpp')

        file_system = FileSystemMock(
            directories={
                project_structure.main_sources_domain_root,
                project_structure.test_sources_domain_root,
            },
            files={
                main_header_math: b'',
                main_source_math: b'',
                test_source_math: b'',
                test_source_lib: b'',
            },
            working_directory=project_structure.project_directory,
        )

        program_arguments = {
            'global': {
                'skip_unit_tests': False
            }
        }

        predicate_result = predicate(
            StagePredicateArguments(file_system=file_system, project_structure=project_structure, program_arguments=program_arguments))
        
        self.assertTrue(predicate_result.can_run)
        
        with StageResources(stage='load_test_sources', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['test_sources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, project_structure=project_structure, resources=resources)
            load_test_sources(stage_arguments)

        expected_test_sources = {
            test_source_math,
            test_source_lib,
        }

        self.assertCountEqual(resources['test_sources'], expected_test_sources)

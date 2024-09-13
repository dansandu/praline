from praline.client.project.pipeline.stages import get_stages

from unittest import TestCase


class StagesTest(TestCase):
    def test_get_stages(self):
        expected_stages = {
            'clean', 
            'compile_main_executable_source',
            'compile_main_sources', 
            'compile_test_sources', 
            'deploy', 
            'format_main_executable_source',
            'format_main_headers', 
            'format_main_sources', 
            'format_test_headers', 
            'format_test_sources', 
            'format', 
            'link_main_executable', 
            'link_main_library', 
            'link_test_executable', 
            'load_clang_format', 
            'load_main_executable_source',
            'load_main_headers', 
            'load_main_resources', 
            'load_main_sources', 
            'load_test_headers', 
            'load_test_resources', 
            'load_test_sources', 
            'main',
            'package', 
            'pull_dependencies', 
            'setup_project', 
            'test', 
        }
        
        stages = get_stages()

        actual_stages = set(stages.keys())
        
        self.assertEqual(actual_stages, expected_stages)

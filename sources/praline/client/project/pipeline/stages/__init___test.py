from praline.client.project.pipeline.stages import get_stages

from unittest import TestCase


class StagesTest(TestCase):
    def test_get_stages(self):
        expected_stages = {
            'load_resources', 
            'deploy', 
            'load_clang_format', 
            'format_test_sources', 
            'load_main_sources', 
            'format', 
            'clean', 
            'pull_dependencies', 
            'format_headers', 
            'format_main_sources', 
            'setup_project', 
            'link_test_executable', 
            'link_main_library', 
            'compile_test_sources', 
            'package', 
            'link_main_executable', 
            'compile_main_sources', 
            'load_headers', 
            'load_test_sources', 
            'test', 
            'main'
        }
        
        stages = get_stages()

        actual_stages = set(stages.keys())
        
        self.assertEqual(actual_stages, expected_stages)

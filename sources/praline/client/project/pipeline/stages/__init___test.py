from praline.client.project.pipeline.stages import get_stages

from unittest import TestCase


class StagesTest(TestCase):
    def test_get_stages(self):
        expected_stages = {
            'clean', 
            'compile_main_executable',
            'compile_main_sources', 
            'compile_test_executable',
            'compile_test_sources', 
            'deploy', 
            'format', 
            'generate_main_farseer_cpp_sources',
            'generate_test_farseer_cpp_sources',
            'link_main_executable', 
            'link_main_library', 
            'link_test_executable',
            'link_test_library', 
            'load_clang_format', 
            'load_project_files',
            'load_test_service',
            'main',
            'package', 
            'pull_dependencies', 
            'setup_project', 
            'test', 
        }

        stages = get_stages()

        actual_stages = set(stages.keys())

        self.assertEqual(actual_stages, expected_stages)

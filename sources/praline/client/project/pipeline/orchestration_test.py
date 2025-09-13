from praline.client.project.pipeline.orchestration import create_pipeline, invoke_stage
from praline.client.project.pipeline.stages import Stage, StageArguments
from praline.common.exception import (
    CyclicStagesException, MultipleSuppliersException, UnsatisfiableStageException
)
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.project_structure import ProjectStructure

import pickle
from os.path import join
from unittest import TestCase


class OrchestrationTest(TestCase):
    def setUp(self):
        self.program_arguments = {'global': {}, 'byStage': {}}

    def create_stage(self, name, requirements, output, exposed=False, cacheable=False, invoker=lambda _: None):
        return Stage(
            name=name,
            requirements=requirements,
            output=output,
            program_arguments=[],
            exposed=exposed,
            cacheable=cacheable,
            invoker=invoker
        )

    def test_create_pipeline(self):
        #
        #        F
        #       / \
        #      D   E
        #     /    |\
        #    A     B C
        #
        stages = {
            'A': self.create_stage('A',         [], ['a']),
            'B': self.create_stage('B',         [], ['b']),
            'C': self.create_stage('C',         [], ['c']),
            'D': self.create_stage('D',      ['a'], ['d']),
            'E': self.create_stage('E', ['b', 'c'], ['e']),
            'F': self.create_stage('F', ['d', 'e'],    []),
        }

        pipeline = create_pipeline('F', stages)

        self.assertEqual(pipeline, ['A', 'D', 'B', 'C', 'E', 'F'])

    def test_create_pipeline_with_cycles(self):
        #
        #   -> C
        #   |  |
        #   |  B
        #   |  |
        #   -- A
        #
        stages = {
            'A': self.create_stage('A', ['c'], ['a']),
            'B': self.create_stage('B', ['a'], ['b']),
            'C': self.create_stage('C', ['b'], ['c']),
        }

        self.assertRaises(CyclicStagesException, create_pipeline, 'C', stages)

    def test_create_pipeline_with_multiple_suppliers(self):
        stages     = {
            'A': self.create_stage('A',    [], ['x']),
            'B': self.create_stage('B',    [], ['x']),
            'C': self.create_stage('C', ['x'], ['c']),
        }

        self.assertRaises(MultipleSuppliersException, create_pipeline, 'C', stages)

    def test_create_pipeline_with_no_suppliers(self):
        stages     = {
            'A': self.create_stage('A',              [], ['a']),
            'B': self.create_stage('B',              [], ['b']),
            'C': self.create_stage('C', ['a', 'b', 'x'], ['c']),
        }

        self.assertRaises(UnsatisfiableStageException, create_pipeline, 'C', stages)

    def test_invoke_stage(self):
        #
        #       A
        #     /   \
        #   B       C -> D
        #   |     / |
        #   E <- F  G    H
        #
        def ai(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(arguments.resources['b'], 'b_value')
            self.assertEqual(arguments.resources['c'], 'c_value')
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['a'] = 'a_value'

        def bi(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(arguments.resources['e'], 'e_value')
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['b'] = 'b_value'

        def ci(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(arguments.resources['d'], 'd_value')
            self.assertEqual(arguments.resources['f'], 'f_value')
            self.assertEqual(arguments.resources['g'], 'g_value')
            self.assertEqual(arguments.program_arguments['byStage']['some-argument'], 'some_value')
            arguments.resources['c'] = arguments.cache['c'] = 'c_value'

        def di(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['d'] = arguments.cache['d'] = 'd_value'

        def ei(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['e'] = arguments.cache['e'] = 'e_value'

        def fi(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(arguments.resources['e'], 'e_value')
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['f'] = arguments.cache['f'] = 'f_value'

        def gi(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['g'] = arguments.cache['g'] = 'g_value'

        def hi(arguments: StageArguments):
            self.fail("stage H shouldn't be invoked")

        stages = {
            'A': self.create_stage('A',      ['b', 'c'], ['a'], False, False, ai),
            'B': self.create_stage('B',           ['e'], ['b'], False, False, bi),
            'C': self.create_stage('C', ['d', 'f', 'g'], ['c'], True,  True,  ci),
            'D': self.create_stage('D',              [], ['d'], False, True,  di),
            'E': self.create_stage('E',              [], ['e'], False, False, ei),
            'F': self.create_stage('F',           ['e'], ['f'], False, False, fi),
            'G': self.create_stage('G',              [], ['g'], False, True,  gi),
            'H': self.create_stage('H',              [], ['h'], False, False, hi),
        }

        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock({
                project_structure.project_directory
            },
            working_directory=project_structure.project_directory
        )

        program_arguments = {
            'global': {},
            'byStage': {'C': { 'some-argument': 'some_value' }}
        }

        invoke_stage(file_system, None, program_arguments, None, project_structure, None, None, 'A', stages)

        cache_path = join('project', 'target', 'cache.pickle')

        expected_cache = {
            'C': {'c': 'c_value'},
            'D': {'d': 'd_value'},
            'G': {'g': 'g_value'},
        }

        self.assertEqual(pickle.loads(file_system.files[cache_path]), expected_cache)

    def test_invoke_stage_with_cycles(self):
        #
        #        A
        #        |
        #   B -> C
        #    ^   |
        #     \_ |
        #        D
        #
        stages = {
            'A': self.create_stage('A', ['c'], ['a']),
            'B': self.create_stage('B', ['c'], ['b']),
            'C': self.create_stage('C', ['d'], ['c']),
            'D': self.create_stage('D', ['b'], ['d']),
        }

        working_directory = 'project'

        file_system = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(CyclicStagesException, invoke_stage, file_system, None, self.program_arguments, None, None, None, None, 'A', stages)

    def test_invoke_stage_with_unsatisfiable_nonexistent_stage(self):
        stages = {
            'A': self.create_stage('A', ['b', 'c'], ['a']),
            'B': self.create_stage('B',      ['d'], ['b']),
            'C': self.create_stage('C',      ['d'], ['c']),
            'D': self.create_stage('D',         [],    []),
        }

        working_directory = 'project'

        file_system = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(UnsatisfiableStageException, invoke_stage, file_system, None, self.program_arguments, None, None, None, None, 'A', stages)

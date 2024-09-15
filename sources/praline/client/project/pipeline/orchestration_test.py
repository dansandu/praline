from praline.client.project.pipeline.orchestration import (create_pipeline, invoke_stage, CyclicStagesError, 
                                                           MultipleSuppliersError, UnsatisfiableStageError)
from praline.client.project.pipeline.stages import Stage, StageArguments, StagePredicateResult
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.project_structure import get_project_structure

import pickle
from os.path import join
from unittest import TestCase


class OrchestrationTest(TestCase):
    def setUp(self):
        self.do_nothing = lambda args: None
        self.can_run    = lambda args: StagePredicateResult.success()
        self.cant_run   = lambda args: StagePredicateResult.failure("can't run")
        self.program_arguments = {'global': {}, 'byStage': {}}

        self.create_pipeline = lambda target_stage, stages: create_pipeline(
            None, None, self.program_arguments, None, None, None, None, target_stage, stages)
        
        self.create_stage = lambda name, requirements, output, predicate: Stage(
            name, requirements, output, predicate, program_arguments=[], exposed=False, cacheable=False, invoker=self.do_nothing
        )

    def test_create_pipeline(self):
        #
        #       [F]
        #        |   
        #      [E D]
        #      /  | \ 
        #    [C] [A][B C]
        #
        stages = {
            'A': self.create_stage('A',                  [], ['a'], self.cant_run),
            'B': self.create_stage('B',                  [], ['b'],  self.can_run),
            'C': self.create_stage('C',                  [], ['c'],  self.can_run),
            'D': self.create_stage('D', [['a'], ['b', 'c']], ['d'],  self.can_run),
            'E': self.create_stage('E',             [['c']], ['e'],  self.can_run),
            'F': self.create_stage('F',        [['e', 'd']],    [],  self.can_run),
        }

        pipeline = self.create_pipeline('F', stages)

        self.assertEqual(pipeline, [(0, 'C'), (0, 'E'), (0, 'B'), (1, 'D'), (0, 'F')])

    def test_create_pipeline_with_cycles(self):
        #
        #   ->[C] 
        #   |  |
        #   | [B]
        #   |  | 
        #   --[A]
        #
        stages = {
            'A': self.create_stage('A', [['c']], ['a'], self.can_run),
            'B': self.create_stage('B', [['a']], ['b'], self.can_run),
            'C': self.create_stage('C', [['b']], ['c'], self.can_run),
        }

        self.assertRaises(CyclicStagesError, self.create_pipeline, 'C', stages)

    def test_create_pipeline_with_multiple_suppliers(self):
        stages     = {
            'A': self.create_stage('A',    [], ['x'], self.can_run),
            'B': self.create_stage('B',    [], ['x'], self.can_run),
            'C': self.create_stage('C', ['x'], ['c'], self.can_run),
        }

        self.assertRaises(MultipleSuppliersError, self.create_pipeline, 'C', stages)

    def test_create_pipeline_with_no_suppliers(self):
        stages     = {
            'A': self.create_stage('A',              [], ['a'], self.can_run),
            'B': self.create_stage('B',              [], ['b'], self.can_run),
            'C': self.create_stage('C', ['a', 'b', 'x'], ['c'], self.can_run),
        }

        self.assertRaises(UnsatisfiableStageError, self.create_pipeline, 'C', stages)

    def test_invoke_stage(self):
        #
        #         [A]
        #        /   \
        #     [B]     [C, D]
        #      |      /|  |  
        #     [E]<-[F][G][H]
        #
        def ai(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(arguments.resources['c'], 'c_value')
            self.assertEqual(arguments.resources['d'], 'd_value')
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['a'] = 'a_value'

        def bi(arguments: StageArguments):
            self.fail("stage B shouldn't be invoked")
        
        def ci(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(arguments.resources['g'], 'g_value')
            self.assertEqual(arguments.program_arguments['byStage']['some-argument'], 'some_value')
            arguments.resources['c'] = arguments.cache['c'] = 'c_value'

        def di(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(arguments.resources['h'], 'h_value')
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['d'] = arguments.cache['d'] = 'd_value'
        
        def ei(arguments: StageArguments):
            self.fail("stage E shouldn't be invoked")

        def fi(arguments: StageArguments):
            self.fail("stage F shouldn't be invoked")

        def gi(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['g'] = arguments.cache['g'] = 'g_value'

        def hi(arguments: StageArguments):
            self.assertEqual(len(arguments.cache), 0)
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['h'] = 'h_value'

        stages = {
            'A': Stage('A', [['b'], ['c', 'd']], ['a'],  self.can_run, [], False, False, ai),
            'B': Stage('B',             [['e']], ['b'],  self.can_run, [], False, False, bi),
            'C': Stage('C',      [['f'], ['g']], ['c'],  self.can_run, [], True,  True,  ci),
            'D': Stage('D',             [['h']], ['d'],  self.can_run, [], False, True,  di),
            'E': Stage('E',                [[]], ['e'], self.cant_run, [], False, False, ei),
            'F': Stage('F',             [['e']], ['f'],  self.can_run, [], False, False, fi),
            'G': Stage('G',                [[]], ['g'],  self.can_run, [], False, True,  gi),
            'H': Stage('H',                [[]], ['h'],  self.can_run, [], False, False, hi),
        }

        project_structure = get_project_structure('project', 'org', 'art')

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
        #         A
        #         |
        #    B -> C
        #     ^   |
        #      \_ |
        #         D
        #
        stages = {
            'A': self.create_stage('A', [['c']], ['a'], self.can_run),
            'B': self.create_stage('B', [['c']], ['b'], self.can_run),
            'C': self.create_stage('C', [['d']], ['c'], self.can_run),
            'D': self.create_stage('D', [['b']], ['d'], self.can_run),
        }

        working_directory = 'project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(CyclicStagesError, invoke_stage, file_system, None, self.program_arguments, None, None, None, None, 'A', stages)

    def test_invoke_stage_with_unsatisfiable_disabled_stage(self):
        stages = {
            'A': self.create_stage('A', [['b', 'c']], ['a'],  self.can_run),
            'B': self.create_stage('B',      [['d']], ['b'],  self.can_run),
            'C': self.create_stage('C',      [['d']], ['c'], self.cant_run),
            'D': self.create_stage('D',         [[]], ['d'],  self.can_run),
        }

        working_directory = 'project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(UnsatisfiableStageError, invoke_stage, file_system, None, self.program_arguments, None, None, None, None, 'A', stages)

    def test_invoke_stage_with_unsatisfiable_nonexistent_stage(self):
        stages = {
            'A': self.create_stage('A', [['b', 'c']], ['a'], self.can_run),
            'B': self.create_stage('B',      [['d']], ['b'], self.can_run),
            'C': self.create_stage('C',      [['d']], ['c'], self.can_run),
            'D': self.create_stage('D',         [[]],    [], self.can_run),
        }

        working_directory = 'project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(UnsatisfiableStageError, invoke_stage, file_system, None, self.program_arguments, None, None, None, None, 'A', stages)

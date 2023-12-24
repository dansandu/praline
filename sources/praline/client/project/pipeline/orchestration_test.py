from praline.client.project.pipeline.orchestration import (create_pipeline, invoke_stage, CyclicStagesError, 
                                                           MultipleSuppliersError, UnsatisfiableStageError)
from praline.client.project.pipeline.stages import Stage, StageArguments, StagePredicateResult
from praline.common.testing.file_system_mock import FileSystemMock

import pickle
from os.path import join
from unittest import TestCase


class OrchestrationTest(TestCase):
    def setUp(self):
        self.do_nothing = lambda args: None
        self.can_run    = lambda args: StagePredicateResult.success()
        self.cant_run   = lambda args: StagePredicateResult.failure("can't run")
        self.program_arguments = {'global': {}, 'byStage': {}}

    def test_create_pipeline(self):
        #
        #       [F]
        #        |   
        #      [E D]
        #      /  | \ 
        #    [C] [A][B C]
        #
        stages = {
            'A': Stage('A',                  [], ['a'], self.cant_run, [], False, False, self.do_nothing),
            'B': Stage('B',                  [], ['b'],  self.can_run, [], False, False, self.do_nothing),
            'C': Stage('C',                  [], ['c'],  self.can_run, [], False, False, self.do_nothing),
            'D': Stage('D', [['a'], ['b', 'c']], ['d'],  self.can_run, [], False, False, self.do_nothing),
            'E': Stage('E',             [['c']], ['e'],  self.can_run, [], False, False, self.do_nothing),
            'F': Stage('F',        [['e', 'd']],    [],  self.can_run, [], False, False, self.do_nothing),
        }

        pipeline = create_pipeline(None, None, self.program_arguments, None, None, None, 'F', stages)

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
            'A': Stage('A', [['c']], ['a'], self.can_run, [], False, False, self.do_nothing),
            'B': Stage('B', [['a']], ['b'], self.can_run, [], False, False, self.do_nothing),
            'C': Stage('C', [['b']], ['c'], self.can_run, [], False, False, self.do_nothing),
        }

        self.assertRaises(CyclicStagesError, 
                          create_pipeline, None, None, self.program_arguments, None, None, None, 'C', stages)

    def test_create_pipeline_with_multiple_suppliers(self):
        stages     = {
            'A': Stage('A',    [], ['x'], self.can_run, [], False, False, self.do_nothing),
            'B': Stage('B',    [], ['x'], self.can_run, [], False, False, self.do_nothing),
            'C': Stage('C', ['x'], ['c'], self.can_run, [], False, False, self.do_nothing),
        }

        self.assertRaises(MultipleSuppliersError, 
                          create_pipeline, None, None, self.program_arguments, None, None, None, 'C', stages)

    def test_create_pipeline_with_no_suppliers(self):
        stages     = {
            'A': Stage('A',              [], ['a'], self.can_run, [], False, False, self.do_nothing),
            'B': Stage('B',              [], ['b'], self.can_run, [], False, False, self.do_nothing),
            'C': Stage('C', ['a', 'b', 'x'], ['c'], self.can_run, [], False, False, self.do_nothing),
        }

        self.assertRaises(UnsatisfiableStageError, 
                          create_pipeline, None, None, self.program_arguments, None, None, None, 'C', stages)

    def test_invoke_stage(self):
        #
        #         [A]
        #        /   \
        #     [B]     [C, D]
        #      |      /|  |  
        #     [E]<-[F][G][H]
        #
        def ai(arguments: StageArguments):
            self.assertIsNone(arguments.cache)
            self.assertEqual(arguments.resources['c'], 'c_value')
            self.assertEqual(arguments.resources['d'], 'd_value')
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['a'] = 'a_value'

        def bi(arguments: StageArguments):
            self.fail("stage B shouldn't be invoked")
        
        def ci(arguments: StageArguments):
            self.assertIsNotNone(arguments.cache)
            self.assertEqual(arguments.resources['g'], 'g_value')
            self.assertEqual(arguments.program_arguments['byStage']['some-argument'], 'some_value')
            arguments.resources['c'] = arguments.cache['c'] = 'c_value'

        def di(arguments: StageArguments):
            self.assertIsNotNone(arguments.cache)
            self.assertEqual(arguments.resources['h'], 'h_value')
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['d'] = arguments.cache['d'] = 'd_value'
        
        def ei(arguments: StageArguments):
            self.fail("stage E shouldn't be invoked")

        def fi(arguments: StageArguments):
            self.fail("stage F shouldn't be invoked")

        def gi(arguments: StageArguments):
            self.assertIsNotNone(arguments.cache)
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['g'] = arguments.cache['g'] = 'g_value'

        def hi(arguments: StageArguments):
            self.assertIsNone(arguments.cache)
            self.assertEqual(len(arguments.program_arguments['byStage']), 0)
            arguments.resources['h'] = 'h_value'

        stages = {
            'A': Stage('A', [['b'], ['c', 'd']], ['a'],  self.can_run, [], False, False, ai),
            'B': Stage('B',             [['e']], ['b'],  self.can_run, [], False, False, bi),
            'C': Stage('C',      [['f'], ['g']], ['c'],  self.can_run, [],  True,  True, ci),
            'D': Stage('D',             [['h']], ['d'],  self.can_run, [],  True, False, di),
            'E': Stage('E',                [[]], ['e'], self.cant_run, [], False, False, ei),
            'F': Stage('F',             [['e']], ['f'],  self.can_run, [],  True, False, fi),
            'G': Stage('G',                [[]], ['g'],  self.can_run, [],  True, False, gi),
            'H': Stage('H',                [[]], ['h'],  self.can_run, [], False, False, hi),
        }

        working_directory = 'project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)
        program_arguments = {
            'global': {},
            'byStage': {'C': { 'some-argument': 'some_value' }}
        }

        invoke_stage(file_system, None, program_arguments, None, None, None, 'A', stages)

        cache_path = join('project', 'target', 'cache.pickle')

        self.assertEqual(pickle.loads(file_system.files[cache_path]), 
                         {'C': {'c': 'c_value'}, 'D': {'d': 'd_value'}, 'G': {'g': 'g_value'}})

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
            'A': Stage('A', [['c']], ['a'], self.can_run, [], False, False, self.do_nothing),
            'B': Stage('B', [['c']], ['b'], self.can_run, [], False, False, self.do_nothing),
            'C': Stage('C', [['d']], ['c'], self.can_run, [],  True, False, self.do_nothing),
            'D': Stage('D', [['b']], ['d'], self.can_run, [],  True, False, self.do_nothing),
        }

        working_directory = 'project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(CyclicStagesError, 
                          invoke_stage, file_system, None, self.program_arguments, None, None, None, 'A', stages)

    def test_invoke_stage_with_unsatisfiable_disabled_stage(self):
        stages = {
            'A': Stage('A', [['b', 'c']], ['a'],  self.can_run, [], False, False, self.do_nothing),
            'B': Stage('B',      [['d']], ['b'],  self.can_run, [], False, False, self.do_nothing),
            'C': Stage('C',      [['d']], ['c'], self.cant_run, [],  True, False, self.do_nothing),
            'D': Stage('D',         [[]], ['d'],  self.can_run, [],  True, False, self.do_nothing),
        }

        working_directory = 'project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(UnsatisfiableStageError, 
                          invoke_stage, file_system, None, self.program_arguments, None, None, None, 'A', stages)

    def test_invoke_stage_with_unsatisfiable_nonexistent_stage(self):
        stages = {
            'A': Stage('A', [['b', 'c']], ['a'], self.can_run, [], False, False, self.do_nothing),
            'B': Stage('B',      [['d']], ['b'], self.can_run, [], False, False, self.do_nothing),
            'C': Stage('C',      [['d']], ['c'], self.can_run, [],  True, False, self.do_nothing),
            'D': Stage('D',         [[]],    [], self.can_run, [],  True, False, self.do_nothing)
        }

        working_directory = 'project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)

        self.assertRaises(UnsatisfiableStageError, 
                          invoke_stage, file_system, None, self.program_arguments, None, None, None, 'A', stages)

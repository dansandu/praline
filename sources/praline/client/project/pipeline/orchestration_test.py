from os.path import normpath
from praline.client.project.pipeline.orchestration import create_pipeline, invoke_stage, CyclicStagesError, MultipleSuppliersError, ResourceNotSuppliedError, UnsatisfiableStageError
from praline.client.project.pipeline.stages.stage import Stage
from praline.common.testing.file_system_mock import FileSystemMock
from io import BytesIO
from typing import Any, IO
from unittest import TestCase
import pickle


class OrchestrationTest(TestCase):
    def test_create_pipeline(self):
        #
        #       [F]
        #        |   
        #      [E D]
        #      /  | \ 
        #    [C] [A][B C]
        #
        do_nothing = lambda f, r, c, a, cfg, rp: None
        can_run    = lambda _, __, ___:  True
        cant_run   = lambda _, __, ___: False
        stages     = {
            'A': Stage('A',                  [], ['a'], cant_run, [], False, False, do_nothing),
            'B': Stage('B',                  [], ['b'],  can_run, [], False, False, do_nothing),
            'C': Stage('C',                  [], ['c'],  can_run, [], False, False, do_nothing),
            'D': Stage('D', [['a'], ['b', 'c']], ['d'],  can_run, [], False, False, do_nothing),
            'E': Stage('E',             [['c']], ['e'],  can_run, [], False, False, do_nothing),
            'F': Stage('F',        [['e', 'd']],    [],  can_run, [], False, False, do_nothing)
        }
        file_system       = FileSystemMock()
        program_arguments = {'global': {}, 'byStage': {}}
        configuration     = {}
        pipeline          = create_pipeline('F', stages, file_system, program_arguments, configuration)

        self.assertEqual(pipeline, [(0, 'C'), (0, 'E'), (0, 'B'), (1, 'D'), (0, 'F')])

    def test_create_pipeline_with_cycles(self):
        #
        #   ->[C] 
        #   |  |
        #   | [B]
        #   |  | 
        #   --[A]
        #
        do_nothing = lambda f, r, c, a, cfg, rp: None
        can_run    = lambda _, __, ___:  True
        stages     = {
            'A': Stage('A', [['c']], ['a'], can_run, [], False, False, do_nothing),
            'B': Stage('B', [['a']], ['b'], can_run, [], False, False, do_nothing),
            'C': Stage('C', [['b']], ['c'], can_run, [], False, False, do_nothing)
        }
        file_system       = FileSystemMock()
        program_arguments = {'global': {}, 'byStage': {}}
        configuration     = {}

        self.assertRaises(CyclicStagesError, create_pipeline, 'C', stages, file_system, program_arguments, configuration)

    def test_create_pipeline_with_multiple_suppliers(self):
        do_nothing = lambda f, r, c, a, cfg, rp: None
        can_run    = lambda _, __, ___:  True
        stages     = {
            'A': Stage('A',    [], ['x'], can_run, [], False, False, do_nothing),
            'B': Stage('B',    [], ['x'], can_run, [], False, False, do_nothing),
            'C': Stage('C', ['x'], ['c'], can_run, [], False, False, do_nothing)
        }
        file_system       = FileSystemMock()
        program_arguments = {'global': {}, 'byStage': {}}
        configuration     = {}

        self.assertRaises(MultipleSuppliersError, create_pipeline, 'C', stages, file_system, program_arguments, configuration)

    def test_create_pipeline_with_no_suppliers(self):
        do_nothing = lambda f, r, c, a, cfg, rp: None
        can_run    = lambda _, __, ___:  True
        stages     = {
            'A': Stage('A',    [], ['a'], can_run, [], False, False, do_nothing),
            'B': Stage('B',    [], ['b'], can_run, [], False, False, do_nothing),
            'C': Stage('C', ['a', 'b', 'x'], ['c'], can_run, [], False, False, do_nothing)
        }
        file_system       = FileSystemMock()
        program_arguments = {'global': {}, 'byStage': {}}
        configuration     = {}

        self.assertRaises(UnsatisfiableStageError, create_pipeline, 'C', stages, file_system, program_arguments, configuration)

    def test_invoke_stage(self):
        #
        #         [A]
        #        /   \
        #     [B]     [C, D]
        #      |      /|  |  
        #     [E]<-[F][G][H]
        #
        def ai(f, r, c, a, cfg, rp):
            self.assertIsNone(c)
            self.assertEqual(r['c'], 'c_value')
            self.assertEqual(r['d'], 'd_value')
            self.assertEqual(len(a['byStage']), 0)
            r['a'] = 'a_value'

        def bi(f, r, c, a, cfg, rp):
            self.fail("stage B shouldn't be invoked")
        
        def ci(f, r, c, a, cfg, rp):
            self.assertIsNotNone(c)
            self.assertEqual(r['g'], 'g_value')
            self.assertEqual(a['byStage']['some-argument'], 'some_value')
            r['c'] = c['c'] = 'c_value'

        def di(f, r, c, a, cfg, rp):
            self.assertIsNotNone(c)
            self.assertEqual(r['h'], 'h_value')
            self.assertEqual(len(a['byStage']), 0)
            r['d'] = c['d'] = 'd_value'
        
        def ei(f, r, c, a, cfg, rp):
            self.fail("stage E shouldn't be invoked")

        def fi(f, r, c, a, cfg, rp):
            self.fail("stage F shouldn't be invoked")

        def gi(f, r, c, a, cfg, rp):
            self.assertIsNotNone(c)
            self.assertEqual(len(a['byStage']), 0)
            r['g'] = c['g'] = 'g_value'

        def hi(f, r, c, a, cfg, rp):
            self.assertIsNone(c)
            self.assertEqual(len(a['byStage']), 0)
            r['h'] = 'h_value'

        can_run  = lambda _, __, ___:  True
        cant_run = lambda _, __, ___: False
        stages   = {
            'A': Stage('A', [['b'], ['c', 'd']], ['a'],  can_run,     [], False, False, ai),
            'B': Stage('B',             [['e']], ['b'],  can_run,     [], False, False, bi),
            'C': Stage('C',      [['f'], ['g']], ['c'],  can_run,     [],  True,  True, ci),
            'D': Stage('D',             [['h']], ['d'],  can_run,     [],  True, False, di),
            'E': Stage('E',                [[]], ['e'], cant_run,     [], False, False, ei),
            'F': Stage('F',             [['e']], ['f'],  can_run,     [],  True, False, fi),
            'G': Stage('G',                [[]], ['g'],  can_run,     [],  True, False, gi),
            'H': Stage('H',                [[]], ['h'],  can_run,     [], False, False, hi)
        }
        working_directory = 'my/project'
        file_system       = FileSystemMock({working_directory}, working_directory=working_directory)
        program_arguments = {
            'global': {},
            'byStage': {'C': { 'some-argument': 'some_value' }}
        }
        invoke_stage('A', stages, file_system, program_arguments, None, None)

        cache_path = normpath('my/project/target/cache.pickle')

        self.assertEqual(pickle.loads(file_system.files[cache_path]), {'C': {'c': 'c_value'}, 'D': {'d': 'd_value'}, 'G': {'g': 'g_value'}})

    def test_invoke_stage_with_cycles(self):
        #
        #         A
        #         |
        #    B -> C
        #     ^   |
        #      \_ |
        #         D
        #
        do_nothing = lambda f, r, c, a, cfg, rp: None
        can_run    = lambda _, __, ___:  True
        stages     = {
            'A': Stage('A', [['c']], ['a'], can_run, [], False, False, do_nothing),
            'B': Stage('B', [['c']], ['b'], can_run, [], False, False, do_nothing),
            'C': Stage('C', [['d']], ['c'], can_run, [],  True, False, do_nothing),
            'D': Stage('D', [['b']], ['d'], can_run, [],  True, False, do_nothing)
        }
        file_system = FileSystemMock()
        program_arguments = {'global': {}, 'byStage': {}}

        self.assertRaises(CyclicStagesError, invoke_stage, 'A', stages, file_system, program_arguments, None, None)

    def test_invoke_stage_with_unsatisfiable_disabled_stage(self):
        do_nothing = lambda f, r, c, a, cfg, rp: None
        can_run    = lambda _, __, ___:  True
        cant_run   = lambda _, __, ___:  False
        stages     = {
            'A': Stage('A', [['b', 'c']], ['a'],  can_run, [], False, False, do_nothing),
            'B': Stage('B',      [['d']], ['b'],  can_run, [], False, False, do_nothing),
            'C': Stage('C',      [['d']], ['c'], cant_run, [],  True, False, do_nothing),
            'D': Stage('D',         [[]], ['d'],  can_run, [],  True, False, do_nothing)
        }
        file_system = FileSystemMock()
        program_arguments = {'global': {}, 'byStage': {}}

        self.assertRaises(UnsatisfiableStageError, invoke_stage, 'A', stages, file_system, program_arguments, None, None)

    def test_invoke_stage_with_unsatisfiable_nonexistent_stage(self):
        do_nothing = lambda f, r, c, a, cfg, rp: None
        can_run    = lambda _, __, ___:  True
        stages     = {
            'A': Stage('A', [['b', 'c']], ['a'],  can_run, [], False, False, do_nothing),
            'B': Stage('B',      [['d']], ['b'],  can_run, [], False, False, do_nothing),
            'C': Stage('C',      [['d']], ['c'],  can_run, [],  True, False, do_nothing),
            'D': Stage('D',         [[]],    [],  can_run, [],  True, False, do_nothing)
        }
        file_system = FileSystemMock()
        program_arguments = {'global': {}, 'byStage': {}}

        self.assertRaises(UnsatisfiableStageError, invoke_stage, 'A', stages, file_system, program_arguments, None, None)

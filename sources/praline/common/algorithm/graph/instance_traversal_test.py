from praline.common.algorithm.graph.instance_traversal import multiple_instance_depth_first_traversal
from unittest import TestCase


class InstanceTraversalTest(TestCase):
    def test_traversal(self):
        #
        #            [A]
        #           /   \
        #           |  [D, E]
        #           | /     \ \
        #        [B, C]     |  |
        #       /    | \    |  |
        #    [F] [G, H][I] [J][K]
        #         |  |
        #        [L][M]
        #
        tree = {
            'A': [['B', 'C'], ['D', 'E']],
            'B': [['F']],
            'C': [['G', 'H'], ['I']],
            'D': [['C']],
            'E': [['J'], ['K']],
            'F': [],
            'G': [['L']],
            'H': [['M']],
            'I': [],
            'J': [],
            'K': [],
            'L': [],
            'M': []
        }

        trees = multiple_instance_depth_first_traversal('A', tree.__getitem__, lambda _, __: True, lambda _: None)

        self.assertEqual(len(trees), 6)

        tree0 = {
            'A': (0, ['B', 'C']),
            'B': (0, ['F']),
            'C': (0, ['G', 'H']),
            'F': (0, []),
            'G': (0, ['L']),
            'H': (0, ['M']),
            'M': (0, []),
            'L': (0, [])
        }

        self.assertEqual(tree0, trees[0])

        tree1 = {
            'A': (1, ['D', 'E']),
            'C': (0, ['G', 'H']),
            'D': (0, ['C']),
            'E': (0, ['J']),
            'J': (0, []),
            'G': (0, ['L']),
            'H': (0, ['M']),
            'L': (0, []),
            'M': (0, [])
        }

        self.assertEqual(tree1, trees[1])

        tree2 = {
            'A': (0, ['B', 'C']),
            'B': (0, ['F']),
            'C': (1, ['I']),
            'F': (0, []),
            'I': (0, [])
        }

        self.assertEqual(tree2, trees[2])

        tree3 = {
            'A': (1, ['D', 'E']),
            'C': (0, ['G', 'H']),
            'D': (0, ['C']),
            'E': (1, ['K']),
            'K': (0, []),
            'G': (0, ['L']),
            'H': (0, ['M']),
            'L': (0, []),
            'M': (0, [])
        }

        self.assertEqual(tree3, trees[3])

        tree4 = {
            'A': (1, ['D', 'E']),
            'C': (1, ['I']),
            'D': (0, ['C']),
            'E': (0, ['J']),
            'I': (0, []),
            'J': (0, [])
        }

        self.assertEqual(tree4, trees[4])

        tree5 = {
            'A': (1, ['D', 'E']),
            'C': (1, ['I']),
            'D': (0, ['C']),
            'E': (1, ['K']),
            'I': (0, []),
            'K': (0, [])
        }

        self.assertEqual(tree5, trees[5])

    def test_traversal_with_cycles(self):
        #
        #            [A]<--------
        #           /   \        \
        #           |  [D, E]     \
        #           | /     \ \   |
        #        [B, C]     |  |  |
        #       /    | \    |  |  |
        #    [F] [G, H][I] [J][K] |
        #                   |_____|
        #
        tree = {
            'A': [['B', 'C'], ['D', 'E']],
            'B': [['F']],
            'C': [['G', 'H'], ['I']],
            'D': [['C']],
            'E': [['J'], ['K']],
            'F': [],
            'G': [],
            'H': [],
            'I': [],
            'J': [['A']],
            'K': []
        }
        cycles = []
        trees = multiple_instance_depth_first_traversal('A', tree.__getitem__, lambda _, __: True, cycles.append)

        self.assertEqual(cycles, [['A', 'E', 'J']])

        self.assertEqual(len(trees), 6)

        tree0 = {
            'A': (0, ['B', 'C']),
            'B': (0, ['F']),
            'C': (0, ['G', 'H']),
            'F': (0, []), 
            'G': (0, []), 
            'H': (0, [])
        }

        self.assertEqual(tree0, trees[0])

        tree1 = {
            'A': (1, ['D', 'E']),
            'C': (0, ['G', 'H']),
            'D': (0, ['C']),
            'E': (0, ['J']),
            'J': (0, []),
            'G': (0, []),
            'H': (0, [])
        }

        self.assertEqual(tree1, trees[1])

        tree2 = {
            'A': (0, ['B', 'C']),
            'B': (0, ['F']),
            'C': (1, ['I']),
            'F': (0, []),
            'I': (0, [])
        }

        self.assertEqual(tree2, trees[2])

        tree3 = {
            'A': (1, ['D', 'E']),
            'C': (0, ['G', 'H']),
            'D': (0, ['C']),
            'E': (1, ['K']),
            'K': (0, []),
            'G': (0, []),
            'H': (0, [])
        }

        self.assertEqual(tree3, trees[3])

        tree4 = {
            'A': (1, ['D', 'E']),
            'C': (1, ['I']),
            'D': (0, ['C']),
            'E': (0, ['J']),
            'I': (0, []),
            'J': (0, [])
        }

        self.assertEqual(tree4, trees[4])

        tree5 = {
            'A': (1, ['D', 'E']),
            'C': (1, ['I']),
            'D': (0, ['C']),
            'E': (1, ['K']),
            'I': (0, []),
            'K': (0, [])
        }

        self.assertEqual(tree5, trees[5])

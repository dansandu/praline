from praline.common.algorithm.graph.simple_traversal import depth_first_traversal, root_last_traversal
from unittest import TestCase


class SimpleTraversalTest(TestCase):
    def test_root_last_traversal(self):
        #
        #           A
        #         / | \
        #        B  C  D
        #       / \ |  |
        #      E    F  G
        #    / | \ /
        #   H  I  J
        #
        tree = {
            'A': ['B', 'C', 'D'],
            'B': ['E', 'F'],
            'C': ['F'],
            'D': ['G'],
            'E': ['H', 'I', 'J'],
            'F': ['J'],
            'G': [],
            'H': [],
            'I': [],
            'J': []
        }

        nodes = root_last_traversal('A', tree.__getitem__)

        self.assertEqual(nodes, ['H', 'I', 'J', 'E', 'F', 'B', 'C', 'G', 'D', 'A'])

    def test_cyclic_root_last_traversal(self):
        #
        #     ----> A
        #     |   / | \
        #     |  B  C  D
        #     | / \ | / \
        #     -E    F -> G
        #   
        tree = {
            'A': ['B', 'C', 'D'],
            'B': ['E', 'F'],
            'C': ['F'],
            'D': ['F', 'G'],
            'E': ['A'],
            'F': ['G'],
            'G': []
        }

        nodes = root_last_traversal('A', tree.__getitem__)

        self.assertEqual(nodes, ['E', 'G', 'F', 'B', 'C', 'D', 'A'])

    def test_depth_first_traversal(self):
        #
        #           A
        #         / | \
        #        B  C  D
        #       / \ |  |
        #      E    F  G
        #    / | \ /
        #   H  I  J
        #
        expected_tree = {
            'A': ['B', 'C', 'D'],
            'B': ['E', 'F'],
            'C': ['F'],
            'D': ['G'],
            'E': ['H', 'I', 'J'],
            'F': ['J'],
            'G': [],
            'H': [],
            'I': [],
            'J': []
        }

        def on_cycle(cycle):
            self.fail(f"cycle detected: {cycle}")

        actual_tree = depth_first_traversal('A', expected_tree.__getitem__, on_cycle)

        self.assertEqual(actual_tree, expected_tree)

    def test_cyclic_depth_first_traversal(self):
        #
        #     ----> A
        #     |   / | \
        #     |  B  C  D
        #     | / \ | / \
        #     -E    F -> G
        #   
        tree = {
            'A': ['B', 'C', 'D'],
            'B': ['E', 'F'],
            'C': ['F'],
            'D': ['F', 'G'],
            'E': ['A'],
            'F': ['G'],
            'G': []
        }
        
        expected_tree = {
            'A': ['B', 'C', 'D'],
            'B': ['E', 'F'],
            'C': ['F'],
            'D': ['F', 'G'],
            'E': [],
            'F': ['G'],
            'G': []
        }

        expected_cycle = ['A', 'B', 'E']

        actual_cycle = []

        def on_cycle(cycle):
            actual_cycle.extend(cycle)

        actual_tree = depth_first_traversal('A', tree.__getitem__, on_cycle)

        self.assertEqual(actual_tree, expected_tree)

        self.assertEqual(actual_cycle, expected_cycle)

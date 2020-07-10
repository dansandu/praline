from praline.common.algorithm.graph.simple_traversal import root_last_traversal
from unittest import TestCase


class RootLastTraversalTest(TestCase):
    def test_traversal(self):
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

    def test_cyclic_traversal(self):
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

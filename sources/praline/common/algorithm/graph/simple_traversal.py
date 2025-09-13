from copy import deepcopy
from typing import Callable, List


def root_last_traversal(root_node: str, children_supplier: Callable[[str], List[str]]) -> List[str]:
    visited = []
    result = []

    def root_last_traversal_work(node: str):
        visited.append(node)
        for child in children_supplier(node):
            if child not in visited:
                root_last_traversal_work(child)
        result.append(node)
    
    root_last_traversal_work(root_node)
    return result


def depth_first_traversal(
    start_node: str, 
    children_supplier: Callable[[str], List[str]],
    on_cycle: Callable[[List[str]], None]
) -> List[str]:
    stack = [(start_node, None)]
    path  = []
    tree  = {}
    while len(stack) > 0:
        node, parent = stack.pop()

        if node in tree:
            children = tree[node]
        else:
            tree[node] = children = deepcopy(children_supplier(node))

        while len(path) > 0 and path[-1] != parent:
            path.pop()

        path.append(node)
        for index in range(len(path)):
            if path[index] in children:
                on_cycle(path[index:])
                children.remove(path[index])

        stack.extend((child, node) for child in children)

    return tree

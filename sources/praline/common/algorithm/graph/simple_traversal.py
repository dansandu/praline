from collections import deque
from praline.common.tracing import trace
from typing import Callable, Dict, List


@trace
def root_last_traversal(root: str, node_visitor: Callable[[str], List[str]]) -> List[str]:
    visited = []
    result = []

    def root_last_traversal_work(node: str):
        visited.append(node)
        for child in node_visitor(node):
            if child not in visited:
                root_last_traversal_work(child)
        result.append(node)
    
    root_last_traversal_work(root)
    return result

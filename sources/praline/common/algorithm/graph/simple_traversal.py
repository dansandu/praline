from collections import deque
from praline.common.tracing import trace


@trace
def root_last_traversal(node, tree):
    visited = []
    result = []

    def root_last_traversal_work(node):
        visited.append(node)
        for child in tree[node]:
            if child not in visited:
                root_last_traversal_work(child)
        result.append(node)
    
    root_last_traversal_work(node)
    return result


def depth_first_traversal(root, visitor, on_cycle):
    chain = []
    children_cache = {}

    def cut_dangling_part_from_chain(parent, current):
        while chain and chain[-1] != parent:
            chain.pop()
        chain.append(current)
        for i in range(len(chain)):
            if chain[i] in children_cache[current]:
                on_cycle(chain[i:])
                children_cache[current].remove(chain[i])
    
    stack = [(None, root)]
    while stack:
        parent, current = stack.pop()
        if current not in children_cache:
            children_cache[current] = visitor(current)
        cut_dangling_part_from_chain(parent, current)
        stack.extend((current, child) for child in children_cache[current])
    return children_cache


def breadth_first_traversal(root, visitor):
    tagged = []
    cache = {}
    queue = deque([root])
    while queue:
        current = queue.popleft()
        tagged.append(current)
        cache[current] = children = visitor(current)
        queue.extend(child for child in children if child not in tagged)
        tagged.extend(children)
    return cache

from dataclasses import dataclass
from typing import Dict, Callable, List, Tuple
from copy import deepcopy


@dataclass
class Instance:
    current_node: str
    parent_node : str
    stack       : List[Tuple[str, str]]
    tree        : Dict[str, Tuple[int, List[str]]]
    chain       : List[str]

    @classmethod
    def copy_from(cls, instance):
        return cls(instance.current_node, instance.parent_node, list(instance.stack), dict(instance.tree), list(instance.chain))

    @classmethod
    def fresh(cls, root: str):
        return cls(None, None, [(root, None)], {}, [])


def remove_dangling_part_from_chain(instance: Instance, on_cycle: Callable[[List[str]], None]) -> None:
    while instance.chain and instance.chain[-1] != instance.parent_node:
        instance.chain.pop()
    instance.chain.append(instance.current_node)
    for i in range(len(instance.chain)):
        current_node_children = instance.tree[instance.current_node][1]
        if instance.chain[i] in current_node_children:
            on_cycle(instance.chain[i:])
            current_node_children.remove(instance.chain[i])


def multiple_instance_depth_first_traversal(start_node        : str,
                                            node_visitor      : Callable[[str], List[List[str]]],
                                            instance_validator: Callable[[str, Dict[str, Tuple[int, List[str]]]], bool],
                                            on_cycle          : Callable[[List[str]], None]) -> List[Dict[str, Tuple[int, List[str]]]]:
    global_tree = {}
    instances   = [Instance.fresh(start_node)]

    def instance_depth_first_traversal(instance: Instance) -> bool:
        if instance.current_node != None:
            if not instance_validator(instance.current_node, instance.tree):
                return False
            remove_dangling_part_from_chain(instance, on_cycle)
            instance.stack.extend((child, instance.current_node) for child in instance.tree[instance.current_node][1])

        while instance.stack:
            instance.current_node, instance.parent_node = instance.stack.pop()
            
            if instance.current_node not in global_tree:
                global_tree[instance.current_node] = children = deepcopy(node_visitor(instance.current_node))
            else:
                children = global_tree[instance.current_node]
            
            if len(children) == 0:
                instance.tree[instance.current_node] = (0, [])
            else:
                instance.tree[instance.current_node] = (0, children[0])
                for i in range(1, len(children)):
                    new_instance = Instance.copy_from(instance)
                    new_instance.tree[new_instance.current_node] = (i, children[i])
                    instances.append(new_instance)
            
            if not instance_validator(instance.current_node, instance.tree):
                return False
            remove_dangling_part_from_chain(instance, on_cycle)
            instance.stack.extend((child, instance.current_node) for child in instance.tree[instance.current_node][1])
        return True

    instance_index = 0
    while instance_index < len(instances):
        if instance_depth_first_traversal(instances[instance_index]):
            instance_index += 1
        else:
            del instances[instance_index]
    return [instance.tree for instance in instances]

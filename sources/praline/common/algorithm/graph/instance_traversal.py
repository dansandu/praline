from dataclasses import dataclass
from typing import Dict, Callable, List, Tuple
from copy import deepcopy


@dataclass
class InstanceValidationResult:
    valid: bool
    explanation: str

    @staticmethod
    def success():
        return InstanceValidationResult(valid=True, explanation=None)
    
    @staticmethod
    def failure(message: str):
        return InstanceValidationResult(valid=False, explanation=message)


@dataclass
class Instance:
    current_node      : str
    parent_node       : str
    stack             : List[Tuple[str, str]]
    tree              : Dict[str, Tuple[int, List[str]]]
    path              : List[str]
    validation_result : InstanceValidationResult

    @classmethod
    def copy_from(cls, instance):
        return cls(instance.current_node, instance.parent_node, list(instance.stack), dict(instance.tree), list(instance.path), instance.validation_result)

    @classmethod
    def fresh(cls, root: str):
        return cls(None, None, [(root, None)], {}, [], InstanceValidationResult.success())


def update_path(instance: Instance, on_cycle: Callable[[List[str]], None]) -> None:
    while instance.path and instance.path[-1] != instance.parent_node:
        instance.path.pop()
    instance.path.append(instance.current_node)
    children = instance.tree[instance.current_node][1]
    for i in range(len(instance.path)):
        if instance.path[i] in children:
            on_cycle(instance.path[i:])
            children.remove(instance.path[i])


def multiple_instance_depth_first_traversal(start_node        : str,
                                            node_visitor      : Callable[[str], List[List[str]]],
                                            instance_validator: Callable[[str, Dict[str, Tuple[int, List[str]]]], InstanceValidationResult],
                                            on_cycle          : Callable[[List[str]], None]) -> List[Instance]:
    global_tree = {}
    instances   = [Instance.fresh(start_node)]

    def instance_depth_first_traversal(instance: Instance):
        if instance.current_node != None:
            instance.validation_result = instance_validator(instance.current_node, instance.tree)
            if not instance.validation_result.valid:
                return
            update_path(instance, on_cycle)
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
            
            instance.validation_result = instance_validator(instance.current_node, instance.tree)
            if not instance.validation_result.valid:
                return
            update_path(instance, on_cycle)
            instance.stack.extend((child, instance.current_node) for child in instance.tree[instance.current_node][1])

    instance_index = 0
    while instance_index < len(instances):
        instance_depth_first_traversal(instances[instance_index])
        instance_index += 1
    
    return instances

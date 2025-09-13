from dataclasses import dataclass
from typing import Dict, Callable, List, Tuple
from copy import deepcopy

import logging


logger = logging.getLogger(__name__)


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


def multiple_instance_depth_first_traversal(
    start_node: str,
    children_supplier: Callable[[str], List[List[str]]],
    instance_validator: Callable[[str, Dict[str, Tuple[int, List[str]]]], InstanceValidationResult],
    on_cycle: Callable[[List[str]], None],
    stop_on_first_valid_instance: bool = False,
    cache_validation: bool = False
) -> List[Instance]:
    global_tree      = {}
    validation_cache = {}
    instances        = [Instance.fresh(start_node)]
    instance_index   = 0

    def instance_depth_first_traversal():
        instance = instances[instance_index]

        if instance.current_node != None:
            if cache_validation and instance.current_node in validation_cache:
                instance.validation_result = validation_cache[instance.current_node]
            else:
                instance.validation_result = instance_validator(instance.current_node, instance.tree, instance.path)
                validation_cache[instance.current_node] = instance.validation_result
            if not instance.validation_result.valid:
                return
            
            update_path(instance, on_cycle)
            instance.stack.extend((child, instance.current_node) for child in instance.tree[instance.current_node][1])

        while instance.stack:
            instance.current_node, instance.parent_node = instance.stack.pop()
            
            if cache_validation and instance.current_node in validation_cache:
                instance.validation_result = validation_cache[instance.current_node]
            else:
                instance.validation_result = instance_validator(instance.current_node, instance.tree, instance.path)
                validation_cache[instance.current_node] = instance.validation_result
            if not instance.validation_result.valid:
                return
            
            if instance.current_node not in global_tree:
                global_tree[instance.current_node] = children = deepcopy(children_supplier(instance.current_node))
            else:
                children = global_tree[instance.current_node]
            
            if len(children) == 0:
                instance.tree[instance.current_node] = (0, [])
            else:
                instance.tree[instance.current_node] = (0, children[0])
                new_instances = []
                for i in range(1, len(children)):
                    new_instance = Instance.copy_from(instance)
                    new_instance.tree[new_instance.current_node] = (i, children[i])
                    new_instances.append(new_instance)
                instances[instance_index+1:instance_index+1] = new_instances
            
            update_path(instance, on_cycle)

            instance.stack.extend((child, instance.current_node) for child in instance.tree[instance.current_node][1])

    while instance_index < len(instances):
        instance_depth_first_traversal()

        if stop_on_first_valid_instance and instances[instance_index].validation_result.valid:
            return instances[:instance_index + 1]

        instance_index += 1
    
    return instances

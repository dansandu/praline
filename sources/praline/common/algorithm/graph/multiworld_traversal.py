
class World:
    def __init__(self, current_node, parent_node, stack, tree, trail):
        self.current_node = current_node
        self.parent_node = parent_node
        self.stack = stack
        self.tree = tree
        self.trail = trail

    @classmethod
    def copy_from(cls, world):
        return cls(world.current_node, world.parent_node, list(world.stack), dict(world.tree), list(world.trail))

    @classmethod
    def fresh(cls, root):
        return cls(None, None, [(None, root)], {}, [])


def cut_dangling_part_from_chain(world, on_cycle):
    while world.trail and world.trail[-1] != world.parent_node:
        world.trail.pop()
    world.trail.append(world.current_node)
    for i in range(len(world.trail)):
        if world.trail[i] in world.tree[world.current_node]:
            on_cycle(world.trail[i:])
            world.tree[world.current_node].remove(world.trail[i])


def world_depth_first_traversal(global_tree, world, visitor, validator, on_new_world, on_cycle):
    if world.current_node != None:
        if not validator(world.current_node, world.tree):
            return False
        cut_dangling_part_from_chain(world, on_cycle)
        world.stack.extend((world.current_node, child) for child in world.tree[world.current_node])

    while world.stack:
        world.parent_node, world.current_node = world.stack.pop()
        
        if world.current_node not in global_tree:
            global_tree[world.current_node] = children = visitor(world.current_node)
        else:
            children = global_tree[world.current_node]
        if len(children) == 0:
            world.tree[world.current_node] = []
        else:
            world.tree[world.current_node] = children[0]
            for i in range(1, len(children)):
                new_world = World.copy_from(world)
                new_world.tree[new_world.current_node] = children[i]
                on_new_world(new_world)
        
        if not validator(world.current_node, world.tree):
            return False
        cut_dangling_part_from_chain(world, on_cycle)
        world.stack.extend((world.current_node, child) for child in world.tree[world.current_node])
    return True


def multiworld_depth_first_traversal(root, visitor, validator, on_cycle):
    global_tree = {}
    worlds = [World.fresh(root)]
    world_index = 0
    while world_index < len(worlds):
        if world_depth_first_traversal(global_tree, worlds[world_index], visitor, validator, lambda w: worlds.append(w), on_cycle):
            world_index += 1
        else:
            del worlds[world_index]
    return worlds

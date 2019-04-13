from praline.common.cache import Cache
from praline.client.project.pipeline.arguments import get_arguments
from praline.client.project.pipeline.dynamic_wiring import deploy_wiring, format_code_wiring, run_unit_tests_wiring
from praline.client.project.pipeline.stage.base import stages
from praline.common.algorithm.graph.simple_traversal import depth_first_traversal, children_count
from praline.common.file_system import current_working_directory, join
from praline.common.tracing import trace


@trace
def get_stage_tree(stages):
    return {parent : [child for child in stages if any(prerequisite in stages[child].produces for prerequisite in stages[parent].consumes)] for parent in stages}


def check_for_cyclic_dependencies(start_stage, stage_tree):
    def on_cycle(cycle):
        raise RuntimeError(f"cyclic dependencies for stages {cycle}")

    def children(stage_name):
        return stage_tree[stage_name]

    return depth_first_traversal(start_stage, visitor=children, on_cycle=on_cycle)


@trace
def create_pipeline(start_stage, stages, run_unit_tests, format_code):
    deploy_wiring(stages)
    if run_unit_tests:
        run_unit_tests_wiring(stages)
    if format_code:
        format_code_wiring(stages)
    stage_tree = get_stage_tree(stages)
    subtree = check_for_cyclic_dependencies(start_stage, stage_tree)
    dependency_count = children_count(start_stage, subtree)
    return sorted([stage_name for stage_name in dependency_count], key=lambda s: dependency_count[s])


class StageResources:
    def __init__(self, stage, data, constrained_produces):
        self.stage = stage
        self.data = data
        self.constrained_produces = constrained_produces

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self)
    
    def __getitem__(self, name):
        if name not in self.data:
            raise RuntimeError(f"stage '{self.stage}' consumes '{name}' but it didn't declare it or it doesn't exist")
        return self.data[name]

    def __setitem__(self, name, value):
        if name not in self.constrained_produces:
            raise RuntimeError(f"stage '{self.stage}' produces '{name}' but it didn't declare it")
        self.data[name] = value


@trace
def conduct():
    data = {}
    arguments = get_arguments(stages)
    pipeline = create_pipeline(arguments['global']['stage'], stages, not arguments['global']['skip_unit_tests'], not arguments['global']['skip_formatting'])
    working_directory = current_working_directory()
    cache_path = join(working_directory, 'target', 'cache.pickle')

    for stage_name in pipeline:
        stage = stages[stage_name]
        stage_data = StageResources(stage_name, {consumed : data[consumed] for consumed in stage.consumes}, stage.produces)
        stage_arguments = dict(arguments['global'])
        if stage.exposed:     
            stage_arguments.update(arguments['byStage'][stage_name])
        if stage.cacheable:
            with Cache(cache_path) as cache:
                cache[stage_name] = stage_cache = cache.get(stage_name, {})
                stage.invoker(working_directory, stage_data, stage_cache, stage_arguments)
        else:
            stage.invoker(working_directory, stage_data, None, stage_arguments)
        for resource in stage.produces:
            if resource not in stage_data.data:
                raise RuntimeError(f"stage '{stage_name}' was expected to produce resource '{resource}' but didn't")
        data.update(stage_data.data)

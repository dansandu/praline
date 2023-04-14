from praline.client.project.pipeline.cache import Cache
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import Stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.algorithm.graph.instance_traversal import multiple_instance_depth_first_traversal
from praline.common.algorithm.graph.simple_traversal import root_last_traversal
from praline.common.file_system import FileSystem, join
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.tracing import trace
from typing import Any, Dict, List


class MultipleSuppliersError(Exception):
    pass


class CyclicStagesError(Exception):
    pass


class UnsatisfiableStageError(Exception):
    pass


class ResourceNotSuppliedError(Exception):
    pass


def get_stage_program_arguments(stage: str, program_arguments: Dict[str, Any]):
    arguments = {
        'global': program_arguments['global'],
        'byStage': program_arguments['byStage'].get(stage, {})
    }
    return arguments


@trace(parameters=[])
def create_pipeline(target_stage: str,
                    stages: Dict[str, Stage],
                    file_system: FileSystem,
                    program_arguments: Dict[str, Any],
                    configuration: Dict[str, Any]) -> List[str]:    
    def on_cycle(cycle: List[str]):
        raise CyclicStagesError(f"cyclic dependencies for stages {cycle}")

    def visitor(stage_name: str):
        requirements_set = stages[stage_name].requirements
        required_stages_set = []
        for requirements in requirements_set:
            required_stages = []
            for requirement in requirements:
                suppliers = [stage.name for stage in stages.values() if requirement in stage.output]
                if not suppliers:
                    raise UnsatisfiableStageError(f"stage '{stage_name}' cannot be satisfied because no stage supplies resource '{requirement}'")
                elif len(suppliers) > 1:
                    raise MultipleSuppliersError(f"resource '{requirement}' is supplied by multiple stages: {', '.join(suppliers)}")
                elif suppliers[0] not in required_stages:
                    required_stages.append(suppliers[0])
            required_stages_set.append(required_stages)
        return required_stages_set

    def validator(stage: str, subtree: Dict[str, List[str]]):
        stage_program_arguments = get_stage_program_arguments(stage, program_arguments)
        return stages[stage].predicate(file_system, stage_program_arguments, configuration)

    trees = multiple_instance_depth_first_traversal(target_stage, visitor, validator, on_cycle)
    if trees:
        stage_subtree = trees[0]
        stage_order   = root_last_traversal(target_stage, lambda n: stage_subtree[n][1])
        pipeline      = [(stage_subtree[stage][0], stage) for stage in stage_order]
        return pipeline
    
    raise UnsatisfiableStageError(f"could not create a pipeline to satisfy stage '{target_stage}'")


@trace
def invoke_stage(target_stage: str, stages: Dict[str, Stage], file_system: FileSystem, program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy) -> None:
    resources = {}
    pipeline = create_pipeline(target_stage, stages, file_system, program_arguments, configuration)
    project_directory = file_system.get_working_directory()
    cache_path = join(project_directory, 'target', 'cache.pickle')

    progress_bar_header_padding = max(len(stage_name) for _, stage_name in pipeline)

    for activation, stage_name in pipeline:
        stage = stages[stage_name]
        stage_resources = StageResources(stage_name, activation, {resource : resources[resource] for resource in stage.requirements[activation]}, stage.output)
        stage_program_arguments = get_stage_program_arguments(stage_name, program_arguments)
        
        progress_bar_header   = stage_name.replace('_', ' ')
        progress_bar_supplier = ProgressBarSupplier(file_system, progress_bar_header, progress_bar_header_padding)
        if stage.cacheable:
            with Cache(file_system, cache_path) as cache:
                cache[stage_name] = stage_cache = cache.get(stage_name, {})
                stage.invoker(file_system, stage_resources, stage_cache, stage_program_arguments, configuration, remote_proxy, progress_bar_supplier)
        else:
            stage.invoker(file_system, stage_resources, None, stage_program_arguments, configuration, remote_proxy, progress_bar_supplier)
        for resource in stage.output:
            if resource not in stage_resources:
                raise ResourceNotSuppliedError(f"stage '{stage_name}' didn't supply resource '{resource}'")
        resources.update(stage_resources.resources)

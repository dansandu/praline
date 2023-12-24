from praline.client.project.pipeline.cache import Cache
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import Stage, StageArguments, StagePredicateArguments
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ArtifactManifest
from praline.common.algorithm.graph.instance_traversal import multiple_instance_depth_first_traversal
from praline.common.algorithm.graph.simple_traversal import root_last_traversal
from praline.common.compiling.compiler import CompilerWrapper
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



def get_stage_program_arguments(stage: str, program_arguments: Dict[str, Any]):
    arguments = {
        'global': program_arguments['global'],
        'byStage': program_arguments['byStage'].get(stage, {})
    }
    return arguments


@trace(parameters=[])
def create_pipeline(file_system: FileSystem,
                    configuration: Dict[str, Any],
                    program_arguments: Dict[str, Any],
                    remote_proxy: RemoteProxy,
                    artifact_manifest: ArtifactManifest,
                    compiler: CompilerWrapper,
                    target_stage: str,
                    stages: Dict[str, Stage]) -> List[str]:    
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
                    raise UnsatisfiableStageError(
                        f"stage '{stage_name}' cannot be satisfied because no stage supplies resource '{requirement}'")
                elif len(suppliers) > 1:
                    raise MultipleSuppliersError(
                        f"resource '{requirement}' is supplied by multiple stages: {', '.join(suppliers)}")
                elif suppliers[0] not in required_stages:
                    required_stages.append(suppliers[0])
            required_stages_set.append(required_stages)
        return required_stages_set

    def validator(stage: str, subtree: Dict[str, List[str]]):
        stage_program_arguments   = get_stage_program_arguments(stage, program_arguments)
        stage_predicate_arguments = StagePredicateArguments(file_system,
                                                            configuration,
                                                            stage_program_arguments,
                                                            remote_proxy,
                                                            artifact_manifest,
                                                            compiler)
        stage_predicate_result = stages[stage].predicate(stage_predicate_arguments)
        return (stage_predicate_result.can_run, stage_predicate_result.explanation)

    instances = multiple_instance_depth_first_traversal(target_stage, visitor, validator, on_cycle)
    valid_trees = [instance.tree for instance in instances if instance.validation_result[0]]
    
    if any(valid_trees):
        stage_subtree = valid_trees[0]
        stage_order   = root_last_traversal(target_stage, lambda n: stage_subtree[n][1])
        pipeline      = [(stage_subtree[stage][0], stage) for stage in stage_order]
        return pipeline
    else:
        message = f"could not create a pipeline to satisfy stage '{target_stage}':\n"
        for index in range(len(instances)):
            instance = instances[index]
            message += f"  for instance #{index} the stage '{instance.current_node}' couldn't run: {instance.validation_result[1]}\n"
        raise UnsatisfiableStageError(message)


@trace
def invoke_stage(file_system: FileSystem,
                 configuration: Dict[str, Any],
                 program_arguments: Dict[str, Any],
                 remote_proxy: RemoteProxy,
                 artifact_manifest: ArtifactManifest,
                 compiler: CompilerWrapper,
                 target_stage: str,
                 stages: Dict[str, Stage]):
    global_resources = {}
    pipeline  = create_pipeline(file_system, 
                                configuration, 
                                program_arguments, 
                                remote_proxy, 
                                artifact_manifest,
                                compiler,
                                target_stage, 
                                stages)

    progress_bar_header_length = max(len(stage_name) for _, stage_name in pipeline)

    for activation, stage_name in pipeline:
        stage = stages[stage_name]
        local_resources = {resource : global_resources[resource] for resource in stage.requirements[activation]}
        stage_program_arguments = get_stage_program_arguments(stage_name, program_arguments)
        with StageResources(stage_name, activation, local_resources, stage.output) as stage_resources:        
            progress_bar_header   = stage_name.replace('_', ' ')
            progress_bar_supplier = ProgressBarSupplier(file_system, progress_bar_header, progress_bar_header_length)
            if stage.cacheable:
                cache_path = join(file_system.get_working_directory(), 'target', 'cache.pickle')
                with Cache(file_system, cache_path) as cache:
                    cache[stage_name] = stage_cache = cache.get(stage_name, {})
                    arguments = StageArguments(file_system=file_system,
                                               configuration=configuration,
                                               program_arguments=stage_program_arguments,
                                               remote_proxy=remote_proxy,
                                               artifact_manifest=artifact_manifest,
                                               compiler=compiler,
                                               resources=stage_resources,
                                               cache=stage_cache,
                                               progress_bar_supplier=progress_bar_supplier)
                    stage.invoker(arguments)
            else:
                arguments = StageArguments(file_system=file_system,
                                           configuration=configuration,
                                           program_arguments=stage_program_arguments,
                                           remote_proxy=remote_proxy,
                                           artifact_manifest=artifact_manifest,
                                           compiler=compiler,
                                           resources=stage_resources,
                                           progress_bar_supplier=progress_bar_supplier)
                stage.invoker(arguments)
            global_resources.update(stage_resources.resources)

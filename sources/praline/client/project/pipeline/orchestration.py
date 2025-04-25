from praline.client.project.pipeline.file_cache import FileCache
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import Stage, StageArguments, StagePredicateArguments
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ArtifactManifest
from praline.common.project_structure import ProjectStructure
from praline.common.algorithm.graph.instance_traversal import InstanceValidationResult, multiple_instance_depth_first_traversal
from praline.common.algorithm.graph.simple_traversal import root_last_traversal
from praline.common.compiling.compiler import Compiler
from praline.common.file_system import FileSystem, join
from praline.common.progress_bar import ProgressBarSupplier

import logging
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


class MultipleSuppliersError(Exception):
    pass


class CyclicStagesError(Exception):
    pass


class UnsatisfiableStageError(Exception):
    pass


def get_stage_program_arguments(stage: str, program_arguments: Dict[str, Any]) -> Dict[str, Any]:
    arguments = {
        'global': program_arguments['global'],
        'byStage': program_arguments['byStage'].get(stage, {})
    }
    return arguments


def create_pipeline(file_system: FileSystem,
                    configuration: Dict[str, Any],
                    program_arguments: Dict[str, Any],
                    remote_proxy: RemoteProxy,
                    project_structure: ProjectStructure,
                    artifact_manifest: ArtifactManifest,
                    compiler: Compiler,
                    target_stage: str,
                    stages: Dict[str, Stage]) -> List[str]:    
    logger.debug(f"Creating pipepline")

    def on_cycle(cycle: List[str]):
        raise CyclicStagesError(f"Cyclic dependencies for stages {cycle}")

    def visitor(stage_name: str):
        requirements_set = stages[stage_name].requirements
        required_stages_set = []
        for requirements in requirements_set:
            required_stages = []
            for requirement in requirements:
                suppliers = [stage.name for stage in stages.values() if requirement in stage.output]
                if not suppliers:
                    raise UnsatisfiableStageError(
                        f"Stage '{stage_name}' cannot be satisfied because no stage supplies resource '{requirement}'")
                elif len(suppliers) > 1:
                    raise MultipleSuppliersError(
                        f"Resource '{requirement}' is supplied by multiple stages: {', '.join(suppliers)}")
                elif suppliers[0] not in required_stages:
                    required_stages.append(suppliers[0])
            required_stages_set.append(required_stages)
        return required_stages_set

    def validator(stage: str, subtree: Dict[str, List[str]], path: List[str]):
        stage_program_arguments   = get_stage_program_arguments(stage, program_arguments)
        stage_predicate_arguments = StagePredicateArguments(
            file_system, configuration, stage_program_arguments, remote_proxy, project_structure, artifact_manifest, compiler)
        
        stage_predicate_result = stages[stage].predicate(stage_predicate_arguments)
        
        if not stage_predicate_result.can_run:
            logger.debug(f"Stage chain {[(subtree[stage][0], stage) for stage in path]} cannot run because: {stage_predicate_result.explanation}")

        return InstanceValidationResult(valid=stage_predicate_result.can_run, explanation=stage_predicate_result.explanation)

    instances = multiple_instance_depth_first_traversal(target_stage, visitor, validator, on_cycle)
    valid_trees = [instance.tree for instance in instances if instance.validation_result.valid]
    
    if any(valid_trees):
        stage_subtree = valid_trees[0]
        stage_order   = root_last_traversal(target_stage, lambda n: stage_subtree[n][1])
        pipeline      = [(stage_subtree[stage][0], stage) for stage in stage_order]
        logger.debug(f"Created pipepline {pipeline}")
        return pipeline
    else:
        message = f"could not create a pipeline to satisfy stage '{target_stage}':\n"
        for index in range(len(instances)):
            instance = instances[index]
            message += f"  for instance #{index} the stage '{instance.current_node}' couldn't run: {instance.validation_result.explanation}\n"
        raise UnsatisfiableStageError(message)


def invoke_stage(file_system: FileSystem,
                 configuration: Dict[str, Any],
                 program_arguments: Dict[str, Any],
                 remote_proxy: RemoteProxy,
                 project_structure: ProjectStructure,
                 artifact_manifest: ArtifactManifest,
                 compiler: Compiler,
                 target_stage: str,
                 stages: Dict[str, Stage]):
    global_resources = {}
    pipeline  = create_pipeline(
        file_system, configuration, program_arguments, remote_proxy, 
        project_structure, artifact_manifest, compiler, target_stage, stages
    )
    
    progress_bar_stage_count = sum(1 for (_, stage_name) in pipeline if stages[stage_name].has_progress_bar)
    progress_bar_stage_index = 1

    for activation, stage_name in pipeline:
        logger.debug(f"Starting stage '{stage_name}'")
        stage = stages[stage_name]
        local_resources = {resource : global_resources[resource] for resource in stage.requirements[activation]}
        stage_program_arguments = get_stage_program_arguments(stage_name, program_arguments)

        with StageResources(stage_name, activation, local_resources, stage.output) as stage_resources:        
            if stage.has_progress_bar:
                progress_bar_supplier = ProgressBarSupplier(file_system, 
                                                            progress_bar_stage_index, 
                                                            progress_bar_stage_count, 
                                                            stage_name)
                progress_bar_stage_index += 1
            else:
                progress_bar_supplier = None

            cache_path = join(project_structure.target_root, 'cache.pickle')

            with FileCache(file_system, cache_path, stage.cacheable) as cache:
                cache[stage_name] = stage_cache = cache.get(stage_name, {})
                arguments = StageArguments(file_system=file_system,
                                           configuration=configuration,
                                           program_arguments=stage_program_arguments,
                                           remote_proxy=remote_proxy,
                                           project_structure=project_structure,
                                           artifact_manifest=artifact_manifest,
                                           compiler=compiler,
                                           resources=stage_resources,
                                           cache=stage_cache,
                                           progress_bar_supplier=progress_bar_supplier)
                stage.invoker(arguments)
            
            global_resources.update(stage_resources.resources)
        
        logger.debug(f"Stage '{stage_name}' has ended")

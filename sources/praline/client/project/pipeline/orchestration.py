from praline.client.project.pipeline.file_cache import FileCache
from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import Stage, StageArguments
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ArtifactManifest
from praline.common.exception import (
    CyclicStagesException, MultipleSuppliersException, UnsatisfiableStageException
)
from praline.common.project_structure import ProjectStructure
from praline.common.algorithm.graph.simple_traversal import depth_first_traversal, root_last_traversal
from praline.common.compiling.compiler import Compiler
from praline.common.file_system import FileSystem, join
from praline.common.progress_bar import ProgressBarSupplier


import logging
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


def get_stage_program_arguments(stage: str, program_arguments: Dict[str, Any]) -> Dict[str, Any]:
    arguments = {
        'global': program_arguments['global'],
        'byStage': program_arguments['byStage'].get(stage, {})
    }
    return arguments


def create_pipeline(target_stage: str, stages: Dict[str, Stage]) -> List[str]:
    logger.debug(f"Creating pipepline")

    def children_supplier(stage_name: str):
        required_stages = []
        for requirement in stages[stage_name].requirements:
            suppliers = [stage.name for stage in stages.values() if requirement in stage.output]
            if len(suppliers) == 0:
                raise UnsatisfiableStageException(
                    f"Stage '{stage_name}' cannot be satisfied because no stage supplies resource '{requirement}'")
            elif len(suppliers) > 1:
                raise MultipleSuppliersException(
                    f"Resource '{requirement}' is supplied by multiple stages: {', '.join(suppliers)}")
            elif suppliers[0] not in required_stages:
                required_stages.append(suppliers[0])
        return required_stages

    def on_cycle(cycle: List[str]):
        raise CyclicStagesException(f"Cyclic dependencies for stages {cycle}")

    stage_subtree = depth_first_traversal(target_stage, children_supplier, on_cycle)

    pipeline = root_last_traversal(target_stage, stage_subtree.__getitem__)

    logger.info(f"Created pipepline {pipeline}")

    return pipeline


def invoke_stage(
    file_system: FileSystem,
    configuration: Dict[str, Any],
    program_arguments: Dict[str, Any],
    remote_proxy: RemoteProxy,
    project_structure: ProjectStructure,
    artifact_manifest: ArtifactManifest,
    compiler: Compiler,
    target_stage: str,
    stages: Dict[str, Stage]
):
    global_resources = {}
    pipeline  = create_pipeline(target_stage, stages)

    for stage_name in pipeline:
        logger.debug(f"Starting stage '{stage_name}'")
        stage = stages[stage_name]
        local_resources = {resource : global_resources[resource] for resource in stage.requirements}
        stage_program_arguments = get_stage_program_arguments(stage_name, program_arguments)

        with StageResources(stage_name, local_resources, stage.output) as stage_resources:        
            progress_bar_supplier = ProgressBarSupplier(file_system, stage_name)

            cache_path = join(project_structure.target_root, 'cache.pickle')

            with FileCache(file_system, cache_path, stage.cacheable) as cache:
                cache[stage_name] = stage_cache = cache.get(stage_name, {})
                arguments = StageArguments(
                    is_target_stage=(target_stage == stage_name),
                    file_system=file_system,
                    configuration=configuration,
                    program_arguments=stage_program_arguments,
                    remote_proxy=remote_proxy,
                    project_structure=project_structure,
                    artifact_manifest=artifact_manifest,
                    compiler=compiler,
                    resources=stage_resources,
                    cache=stage_cache,
                    progress_bar_supplier=progress_bar_supplier
                )
                stage.invoker(arguments)
            
            global_resources.update(stage_resources.resources)
        
        logger.debug(f"Stage '{stage_name}' has ended")

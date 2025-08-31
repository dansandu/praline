from praline.common import ArtifactManifest, ServiceConfiguration
from praline.common.file_system import basename


def get_service_runner_executable(
        artifact_manifest: ArtifactManifest,
        service_configuration: ServiceConfiguration,
        resources):
    service_runner_executable = None
    if service_configuration.executable_to_run != None:
        root_prefix = artifact_manifest.organization + '-' + artifact_manifest.artifact
        if service_configuration.executable_to_run == root_prefix and 'main_executable' in resources:
            service_runner_executable = resources['main_executable']
        else:
            service_runner_executables = [
                exe for exe in resources['external_executables']
                    if basename(exe).startswith(service_configuration.executable_to_run)
            ]

            if len(service_runner_executables) == 0:
                raise RuntimeError(
                    f"No executable was found matching the service runner '{service_configuration.executable_to_run}'. Make sure to add it as a dependency.")
            elif len(service_runner_executables) > 1:
                raise RuntimeError(
                    f"Multiple executables were found matching the service runner '{service_configuration.executable_to_run}'")

            service_runner_executable = service_runner_executables[0]

    return service_runner_executable


def get_test_service_runner_executable(artifact_manifest: ArtifactManifest, resources):
    return get_service_runner_executable(artifact_manifest, artifact_manifest.test_service, resources)

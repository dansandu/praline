from praline.common import ServiceConfiguration
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from typing import Any, Dict


def get_artifact_prefix(artifact: Dict[str, Any]):
    return artifact.get('organization', '') + '-' + artifact.get('artifact', '')


def validate_service(pralinefile: Dict[str, Any], key: str, default_service_configuration: ServiceConfiguration):
    service_runner = pralinefile.get(key)

    if service_runner != None and not isinstance(service_runner, dict):
        raise PralinefileValidationError("Pralinefile service runner has invalid " +
                                         f"type '{type(service_runner)}' -- type must be dict")    

    if service_runner != None:
        allowed_fields = {'executable_to_run', 'library_to_load', 'service_name'}

        for field in service_runner:
            if field not in allowed_fields:
                raise PralinefileValidationError(f"Pralinefile {key} field has unrecognized field {field}")

        executable_to_run = service_runner.get('executable_to_run')

        if executable_to_run == None:
            raise PralinefileValidationError(f"Pralinefile {key} is missing mandatory executable_to_run field")
        
        if not isinstance(executable_to_run, str):
            raise PralinefileValidationError(
                f"Pralinefile {key} executable_to_run has invalid type '{type(executable_to_run)}' -- type must be str")

        def check_if_prefix_is_dependency(prefix):
            is_dependency = False
            for dependency in pralinefile.get('dependencies', []):
                dependency_prefix = get_artifact_prefix(dependency)
                if prefix == dependency_prefix:
                    is_dependency = True
                    break
            if not is_dependency:
                root_prefix = get_artifact_prefix(pralinefile)
                if prefix != root_prefix:
                    raise PralinefileValidationError(
                        f"Pralinefile {key} must be the root artifact or one of its dependencies")
                
        check_if_prefix_is_dependency(executable_to_run)

        library_to_load = service_runner.get('library_to_load', None)

        if library_to_load != None and not isinstance(library_to_load, str):
            raise PralinefileValidationError(
                f"Pralinefile {key} library_to_load has invalid type '{type(library_to_load)}' -- type must be str")

        if library_to_load != None:
            check_if_prefix_is_dependency(library_to_load)

        service_name = service_runner.get('service_name')

        if service_name == None:
            raise PralinefileValidationError(f"Pralinefile {key} is missing mandatory service_name field")
        
        if not isinstance(service_name, str):
            raise PralinefileValidationError(
                f"Pralinefile {key} service_name has invalid type '{type(service_name)}' -- type must be str")
    
        pralinefile[key] = ServiceConfiguration(
            executable_to_run=executable_to_run,
            library_to_load=library_to_load,
            service_name=service_name
        )
    else:
        pralinefile[key] = default_service_configuration

from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_test_service_runner(pralinefile: Dict[str, Any]):
    test_service_runner = pralinefile.get('test_service_runner', None)
    if test_service_runner != None and not isinstance(test_service_runner, str):
        raise PralinefileValidationError("Pralinefile test service runner has invalid " +
                                         f"type '{type(test_service_runner)}' -- type must be str")    
    pralinefile['test_service_runner'] = test_service_runner

    if test_service_runner != None:
        service_runner_is_dependency = False
        for dependency in pralinefile.get('dependencies', []):
            dependency_prefix = dependency.get('organization', '') + '-' + dependency.get('artifact', '')
            if test_service_runner == dependency_prefix:
                service_runner_is_dependency = True
                break
        if not service_runner_is_dependency:
            root_prefix = pralinefile.get('organization', '') + '-' + pralinefile.get('artifact', '')
            if test_service_runner != root_prefix:
                raise PralinefileValidationError("Pralinefile test service runner must be the root artifact or one of its dependencies")

from praline.common.exception import PralinefileValidationException
from praline.common.pralinefile.validation.validator import validator
from typing import Any, Dict


allowed_fields = [
    'organization', 
    'artifact', 
    'version', 
    'platforms', 
    'architectures', 
    'modes',
    'compilers',
    'exported_symbols',
    'artifact_type',
    'main_service',
    'test_service',
    'dependencies'
]


allowed_dependency_fields = [
    'organization', 
    'artifact', 
    'scope', 
    'version'
]


@validator
def validate_allowed_fields(pralinefile: Dict[str, Any]):
    for field in pralinefile:
        if field not in allowed_fields:
            raise PralinefileValidationException(
                f"Pralinefile has unrecognized field '{field}' -- allowed fields are {allowed_fields}")
    pralinefile['dependencies'] = dependencies = pralinefile.get('dependencies', [])
    for dependency in dependencies:
        for field in dependency:
            if field not in allowed_dependency_fields:
                raise PralinefileValidationException(
                    f"Pralinefile dependency has unrecognized field '{field}' -- allowed fields are " +
                    str(allowed_dependency_fields))

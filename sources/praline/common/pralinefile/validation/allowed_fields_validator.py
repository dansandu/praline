from praline.common.pralinefile.constants import allowed_dependency_fields, allowed_pralinefile_fields
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


@validator
def validate_allowed_fields(pralinefile):
    if not isinstance(pralinefile, dict):
        raise PralinefileValidationError(f"pralinefile has invalid type '{type(pralinefile)}' -- type must be dictionary")
    for field in pralinefile:
        if field not in allowed_pralinefile_fields:
            raise PralinefileValidationError(f"pralinefile has unrecognized field '{field}'  -- allowed fields are {allowed_pralinefile_fields}")

    dependencies = pralinefile['dependencies']
    if not isinstance(dependencies, list):
        raise PralinefileValidationError(f"pralinefile dependencies {dependencies} has invalid type '{type(dependencies)}' -- type must be list")
    for dependency in dependencies:
        if not isinstance(pralinefile, dict):
            raise PralinefileValidationError(f"pralinefile dependency {dependency} has invalid type '{type(dependency)}' -- type must be dictionary")
        for field in dependency:
            if field not in allowed_dependency_fields:
                raise PralinefileValidationError(f"pralinefile dependency {dependency} has unrecognized field '{field}'  -- allowed fields are {allowed_dependency_fields}")

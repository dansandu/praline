from praline.common.pralinefile.constants import allowed_dependency_scopes
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


@validator
def scope_validator(pralinefile):
    for dependency in pralinefile['dependencies']:
        if dependency['scope'] not in allowed_dependency_scopes:
            raise PralinefileValidationError(f"pralinefile dependency {dependency} has unrecognized scope '{dependency['scope']}' -- allowed scopes are {allowed_dependency_scopes}")

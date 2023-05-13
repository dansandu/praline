from praline.common import DependencyScope
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_scope(pralinefile: Dict[str, Any]):
    allowed_scopes = [scope.value for scope in DependencyScope]
    for dependency in pralinefile.get('dependencies', []):
        scope = dependency.get('scope', DependencyScope.main.value)
        if not isinstance(scope, str):
            raise PralinefileValidationError(
                f"Pralinefile dependency scope '{scope}' has invalid type '{type(scope)}' -- type must be str")
        if scope not in allowed_scopes:
            raise PralinefileValidationError(
                f"Pralinefile dependency scope '{scope}' is not recognized -- allowed scopes are {allowed_scopes}")
        dependency['scope'] = DependencyScope(scope)

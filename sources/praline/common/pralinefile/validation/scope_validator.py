from praline.common.constants import allowed_dependency_scopes
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_scope(pralinefile: Dict[str, Any]):
    for dependency in pralinefile.get('dependencies', []):
        if dependency.get('scope', 'main') not in allowed_dependency_scopes:
            raise PralinefileValidationError(f"pralinefile dependency {dependency} has unrecognized scope '{dependency['scope']}' -- allowed scopes are {allowed_dependency_scopes}")

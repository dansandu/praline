from praline.common.constants import allowed_pralinefile_fields, allowed_pralinefile_dependency_fields
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_allowed_fields(pralinefile: Dict[str, Any]):
    for field in pralinefile:
        if field not in allowed_pralinefile_fields:
            raise PralinefileValidationError(f"pralinefile has unrecognized field '{field}'  -- allowed fields are {allowed_pralinefile_fields}")
    dependencies = pralinefile.get('dependencies', [])
    for dependency in dependencies:
        for field in dependency:
            if field not in allowed_pralinefile_dependency_fields:
                raise PralinefileValidationError(f"pralinefile dependency {dependency} has unrecognized field '{field}'  -- allowed fields are {allowed_pralinefile_dependency_fields}")

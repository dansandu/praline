from praline.common.constants import mandatory_fields
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_mandatory_fields(pralinefile: Dict[str, Any]):
    for mandatory_field in mandatory_fields:
        if mandatory_field not in pralinefile:
            raise PralinefileValidationError(f"pralinefile doesn't have mandatory field '{mandatory_field}'")
    dependencies = pralinefile.get('dependencies', [])
    for dependency in dependencies:
        for mandatory_field in mandatory_fields:
            if mandatory_field not in dependency:
                raise PralinefileValidationError(f"pralinefile dependency {dependency} doesn't have mandatory field '{mandatory_field}'")

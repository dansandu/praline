from praline.common import Architecture
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_architecture(pralinefile: Dict[str, Any]):
    allowed_architectures = [architecture.value for architecture in Architecture]
    architectures = pralinefile.get('architectures', allowed_architectures)
    if not isinstance(architectures, list):
        raise PralinefileValidationError(
            f"Pralinefile architectures field has invalid type '{type(architectures)}' -- type must be list")
    if not architectures:
        raise PralinefileValidationError(f"Pralinefile architectures field cannot be empty")
    converted_architectures = []
    for architecture in architectures:
        if architecture not in allowed_architectures:
            raise PralinefileValidationError(
                f"Pralinefile architecture '{architecture}' is not recognized -- allowed architectures are " +
                str(allowed_architectures))
        converted_architectures.append(Architecture(architecture))
    pralinefile['architectures'] = converted_architectures

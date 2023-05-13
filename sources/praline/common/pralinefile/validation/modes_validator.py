from praline.common import Mode
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_mode(pralinefile: Dict[str, Any]):
    allowed_modes = [mode.value for mode in Mode]
    modes = pralinefile.get('modes', allowed_modes)
    if not isinstance(modes, list):
        raise PralinefileValidationError(
            f"Pralinefile modes field has invalid type '{type(modes)}' -- type must be list")
    if not modes:
        raise PralinefileValidationError("Pralinefile modes field cannot be empty")
    converted_modes = []
    for mode in modes:
        if mode not in allowed_modes:
            raise PralinefileValidationError(
                f"Pralinefile mode '{mode}' is not recognized -- allowed modes are {allowed_modes}")
        converted_modes.append(Mode(mode))
    pralinefile['modes'] = converted_modes

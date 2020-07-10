from praline.common.constants import allowed_modes
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_mode(pralinefile: Dict[str, Any]):
    modes = pralinefile.get('modes', allowed_modes)
    if not modes:
        raise PralinefileValidationError("pralinefile modes field cannot be empty")
    if not isinstance(modes, list):
        raise PralinefileValidationError(f"pralinefile modes {modes} has invalid type '{type(modes)}' -- type must be list")
    for mode in modes:        
        if mode not in allowed_modes:
            raise PralinefileValidationError(f"pralinefile has unrecognized mode '{mode}' -- allowed modes are {allowed_modes}")

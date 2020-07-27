from praline.common.constants import allowed_compilers
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_compilers(pralinefile: Dict[str, Any]):
    compilers = pralinefile.get('compilers', allowed_compilers)
    if not compilers:
        raise PralinefileValidationError("pralinefile compilers field cannot be empty")
    if not isinstance(compilers, list):
        raise PralinefileValidationError(f"pralinefile compilers {compilers} has invalid type '{type(compilers)}' -- type must be list")
    for compiler in compilers:
        if compiler not in allowed_compilers:
            raise PralinefileValidationError(f"pralinefile çompiler '{compiler}' is not recognized -- allowed compilers are {allowed_compilers}")

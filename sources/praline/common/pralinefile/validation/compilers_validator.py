from praline.common.compiler.base import get_compilers
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


@validator
def validate_compilers(pralinefile):
    allowed_compilers = [c.name() for c in get_compilers()]
    compilers = pralinefile['compilers']
    if not isinstance(compilers, list):
        raise PralinefileValidationError(f"pralinefile compilers {compilers} has invalid type '{type(compilers)}' -- type must be list")
    for compiler in compilers:
        if compiler not in allowed_compilers:
            raise PralinefileValidationError(f"pralinefile çompiler '{compiler}' is not recognized -- allowed compilers are {allowed_compilers}")

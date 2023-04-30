from praline.common import Compiler
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_compilers(pralinefile: Dict[str, Any]):
    allowed_compilers = [compiler.value for compiler in Compiler]
    compilers = pralinefile.get('compilers', allowed_compilers)
    if not isinstance(compilers, list):
        raise PralinefileValidationError(
            f"pralinefile compilers {compilers} has invalid type '{type(compilers)}' -- type must be list")
    if not compilers:
        raise PralinefileValidationError("pralinefile compilers field cannot be empty")
    converted_compilers = []
    for compiler in compilers:
        if compiler not in allowed_compilers:
            raise PralinefileValidationError(
                f"pralinefile çompiler '{compiler}' is not recognized -- allowed compilers are {allowed_compilers}")
        converted_compilers.append(Compiler(compiler))
    pralinefile['compilers'] = converted_compilers

from praline.common.pralinefile.constants import allowed_architectures
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


@validator
def validate_architecture(pralinefile):
    architectures = pralinefile['architectures']
    if not isinstance(architectures, list):
        raise PralinefileValidationError(f"pralinefile architectures {architectures} has invalid type '{type(architectures)}' -- type must be list")
    for architecture in architectures:
        if architecture not in allowed_architectures:
            raise PralinefileValidationError(f"pralinefile architecture '{architecture}' is not recognized -- allowed architectures are {allowed_architectures}")

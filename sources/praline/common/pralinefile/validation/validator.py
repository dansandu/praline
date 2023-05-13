from praline.common.tracing import trace

import functools


registered_validators = []


class PralinefileValidationError(Exception):
    pass


def validator(function):
    registered_validators.append(function)
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapper


@trace(validators=[validator.__name__ for validator in registered_validators])
def validate(pralinefile):
    if not isinstance(pralinefile, dict):
        raise PralinefileValidationError(
            f"Pralinefile has invalid type '{type(pralinefile)}' -- type must be dictionary")
    for validator in registered_validators:
        validator(pralinefile)

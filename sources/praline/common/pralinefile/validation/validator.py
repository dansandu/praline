from functools import wraps
from praline.common.tracing import trace

validators = []


class PralinefileValidationError(Exception):
    pass


def validator(function):
    validators.append(function)
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapper


@trace(validators=[validator.__name__ for validator in validators])
def validate(pralinefile):
    if not isinstance(pralinefile, dict):
        raise PralinefileValidationError(f"invalid {type(pralinefile)} type for pralinefile")
    for validator in validators:
        validator(pralinefile)

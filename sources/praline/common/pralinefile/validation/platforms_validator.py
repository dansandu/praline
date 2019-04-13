from praline.common.pralinefile.constants import allowed_platforms
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


@validator
def validate_platforms(pralinefile):
    platforms = pralinefile.get('platforms')
    if not isinstance(platforms, list):
        raise PralinefileValidationError(f"pralinefile platforms {platforms} has invalid type '{type(platforms)}' -- type must be list")
    for platform in platforms:
        if platform not in allowed_platforms:
            raise PralinefileValidationError(f"pralinefile platform '{platform}' is not recognized -- allowed platforms are {allowed_platforms}")

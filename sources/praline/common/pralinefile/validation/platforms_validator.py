from praline.common.constants import allowed_platforms
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_platforms(pralinefile: Dict[str, Any]):
    platforms = pralinefile.get('platforms', allowed_platforms)
    if not platforms:
        raise PralinefileValidationError("pralinefile platforms field cannot be empty")
    if not isinstance(platforms, list):
        raise PralinefileValidationError(f"pralinefile platforms {platforms} has invalid type '{type(platforms)}' -- type must be list")
    for platform in platforms:
        if platform not in allowed_platforms:
            raise PralinefileValidationError(f"pralinefile platform '{platform}' is not recognized -- allowed platforms are {allowed_platforms}")

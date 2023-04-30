from praline.common import Platform
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_platforms(pralinefile: Dict[str, Any]):
    allowed_platforms = [platform.value for platform in Platform]
    platforms = pralinefile.get('platforms', allowed_platforms)
    if not isinstance(platforms, list):
        raise PralinefileValidationError(
            f"Pralinefile platforms field has invalid type '{type(platforms)}' -- type must be list")
    if not platforms:
        raise PralinefileValidationError(f"Pralinefile platforms field cannot be empty")
    converted_platforms = []
    for platform in platforms:
        if platform not in allowed_platforms:
            raise PralinefileValidationError(f"Pralinefile platform '{platform}' is not recognized -- allowed "
                                             "architectures are {allowed_platforms}")
        converted_platforms.append(Platform(platform))
    pralinefile['platforms'] = converted_platforms

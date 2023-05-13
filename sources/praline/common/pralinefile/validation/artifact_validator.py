from praline.common import artifact_pattern
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


def validate_artifact_work(pralinefile: Dict[str, Any]):
    artifact = pralinefile.get('artifact')
    if artifact == None:
        raise PralinefileValidationError(f"Pralinefile is missing mandatory artifact field")
    if not isinstance(artifact, str):
        raise PralinefileValidationError(
            f"Pralinefile artifact '{artifact}' has invalid type '{type(artifact)}' -- type must be str")
    if not artifact_pattern.fullmatch(artifact):
        raise PralinefileValidationError(
            f"pralinefile artifact '{artifact}' is not valid -- artifact must contain lowercase alphanumerics "
            "or underscores")


@validator
def validate_artifact(pralinefile: Dict[str, Any]):
    validate_artifact_work(pralinefile)
    for dependency in pralinefile.get('dependencies', []):
        validate_artifact_work(dependency)

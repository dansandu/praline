from praline.common.constants import artifact_pattern
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


def validate_root_artifact(pralinefile: Dict[str, Any]):
    artifact = pralinefile.get('artifact', '')
    if not isinstance(artifact, str):
        raise PralinefileValidationError(f"pralinefile artifact '{artifact}' has invalid type '{type(artifact)}' -- type must be str")
    if not artifact_pattern.fullmatch(artifact):
        raise PralinefileValidationError(f"pralinefile artifact '{artifact}' is not valid -- artifact should contain lowercase words separated by underscores")


def validate_dependencies_artifact(pralinefile: Dict[str, Any]):
    for dependency in pralinefile.get('dependencies', []):
        validate_root_artifact(dependency)


@validator
def validate_artifact(pralinefile: Dict[str, Any]):
    validate_root_artifact(pralinefile)
    validate_dependencies_artifact(pralinefile)

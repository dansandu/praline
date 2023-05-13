from praline.common import ArtifactType
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_artifact_type(pralinefile: Dict[str, Any]):
    allowed_artifact_types = [a.value for a in ArtifactType]
    artifact_type = pralinefile.get('artifact_type', ArtifactType.library.value)
    if not isinstance(artifact_type, str):
        raise PralinefileValidationError(
            f"Pralinefile artifact_type field has invalid type '{type(artifact_type)}' -- type must be str")
    if artifact_type not in allowed_artifact_types:
        raise PralinefileValidationError(
                f"Pralinefile artifact_type '{artifact_type}' is not recognized -- allowed values are "
                f"{allowed_artifact_types}")
    pralinefile['artifact_type'] = ArtifactType(artifact_type)

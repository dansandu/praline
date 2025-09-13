from praline.common import ArtifactType
from praline.common.exception import PralinefileValidationException
from praline.common.pralinefile.validation.validator import validator
from typing import Any, Dict


@validator
def validate_artifact_type(pralinefile: Dict[str, Any]):
    allowed_artifact_types = [a.value for a in ArtifactType]
    artifact_type = pralinefile.get('artifact_type', ArtifactType.library.value)
    if not isinstance(artifact_type, str):
        raise PralinefileValidationException(
            f"Pralinefile artifact_type field has invalid type '{type(artifact_type)}' -- type must be str")
    if artifact_type not in allowed_artifact_types:
        raise PralinefileValidationException(
                f"Pralinefile artifact_type '{artifact_type}' is not recognized -- allowed values are "
                f"{allowed_artifact_types}")
    pralinefile['artifact_type'] = ArtifactType(artifact_type)

from praline.common import ArtifactPrefix, ServiceConfiguration
from praline.common.pralinefile.validation.validator import validator
from praline.common.pralinefile.validation.service_validator import validate_service
from typing import Any, Dict


default_service_configuration = ServiceConfiguration(
    executable_to_run=ArtifactPrefix('dansandu-service_runner'),
    library_to_load=None,
    service_name=None
)


@validator
def validate_main_service(pralinefile: Dict[str, Any]):
    validate_service(pralinefile, 'main_service', default_service_configuration=default_service_configuration)

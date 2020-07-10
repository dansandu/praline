from praline.common.constants import allowed_architectures, allowed_compilers, allowed_platforms, allowed_modes
from praline.common.file_system import FileSystem
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validate
from typing import Any, Dict, IO
import yaml


def pralinefile_from_path(file_system : FileSystem, path: str, skip_validation=False) -> Dict[str, Any]:
    with file_system.open_file(path, 'r') as reader:
        return pralinefile_from_reader(reader)


def pralinefile_from_reader(reader: IO[Any], skip_validation=False) -> Dict[str, Any]:
    pralinefile                  = yaml.load(reader.read(), Loader=yaml.SafeLoader)
    pralinefile['architectures'] = pralinefile.get('architectures', allowed_architectures)
    pralinefile['compilers']     = pralinefile.get('compilers', allowed_compilers)
    pralinefile['platforms']     = pralinefile.get('platforms', allowed_platforms)
    pralinefile['modes']         = pralinefile.get('modes', allowed_modes)
    pralinefile['dependencies']  = dependencies = pralinefile.get('dependencies', [])
    for dependency in dependencies:
        dependency['scope'] = dependency.get('scope', 'main')
    if not skip_validation:
        validate(pralinefile)
    return pralinefile

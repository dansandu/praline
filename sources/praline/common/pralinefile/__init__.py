from praline.common.file_system import FileSystem
from praline.common.pralinefile.validation.validator import validate

from typing import Any, Dict
import yaml


def read_pralinefile(file_system: FileSystem, path: str) -> Dict[str, Any]:
    with file_system.open_file(path, 'r') as reader:
        pralinefile = yaml.load(reader.read(), Loader=yaml.SafeLoader)
    validate(pralinefile)
    return pralinefile

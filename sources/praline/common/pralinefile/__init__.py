import yaml
from praline.common.compiler.base import get_compilers
from praline.common.pralinefile.constants import allowed_architectures, allowed_platforms
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validate


def fill(pralinefile):
    for mandatory_field in ['organization', 'artifact', 'version']:
        if mandatory_field not in pralinefile:
            raise PralinefileValidationError(f"pralinefile doesn't have mandatory field '{mandatory_field}'")

    pralinefile['architectures'] = pralinefile.get('architectures', allowed_architectures)
    pralinefile['compilers'] = pralinefile.get('compilers', [compiler.name() for compiler in get_compilers()])
    pralinefile['platforms'] = pralinefile.get('platforms', allowed_platforms)    
    pralinefile['dependencies'] = dependencies = pralinefile.get('dependencies', [])
    for dependency in dependencies:
        for mandatory_field in ['organization', 'artifact', 'version']:
            if mandatory_field not in dependency:
                raise PralinefileValidationError(f"pralinefile dependency {dependency} doesn't have mandatory field '{mandatory_field}'")
        dependency['scope'] = dependency.get('scope', 'main')


def pralinefile_from_path(path, skip_validation=False):
    with open(path, 'r') as reader:
        return pralinefile_from_reader(reader)


def pralinefile_from_reader(reader, skip_validation=False):
    pralinefile = yaml.load(reader.read(), Loader=yaml.SafeLoader)
    fill(pralinefile)
    if not skip_validation:
        validate(pralinefile)
    return pralinefile

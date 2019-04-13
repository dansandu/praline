from praline.common.pralinefile.validation.validator import validator, PralinefileValidationError


@validator
def check_for_duplicated_dependencies(pralinefile):
    ds = pralinefile['dependencies']
    if any(d['organization'] == pralinefile['organization'] and d['artifact'] == pralinefile['artifact'] for d in ds):
        raise PralinefileValidationError(f"pralinefile cannot have itself as a dependency")    
    duplicates = [(i, j) for i in range(len(ds)) for j in range(i + 1, len(ds)) if ds[i]['organization'] == ds[j]['organization'] and ds[i]['artifact'] == ds[j]['artifact']]
    for duplicate in duplicates:
        raise PralinefileValidationError(f"pralinefile cannot have duplicate dependencies -- dependency {ds[duplicate[0]]} is in conflict with dependency {ds[duplicate[1]]}")

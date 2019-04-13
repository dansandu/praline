from re import compile as compile_regex


allowed_pralinefile_fields = ['artifact', 'organization', 'version', 'platforms', 'architectures', 'compilers', 'dependencies']

allowed_dependency_fields = ['artifact', 'organization', 'scope', 'version']

organization_pattern = compile_regex(r"[a-z]+(_[a-z]+)*")

artifact_pattern = compile_regex(r"[a-z]+(_[a-z]+)*")

allowed_architectures = ['arm', 'x86', 'x86_64']

allowed_platforms = ['windows', 'linux', 'darwin']

version_regex = r'(?P<major>[1-9]\d*|\d)\.(?P<minor_wildcard>\+)?(?P<minor>[1-9]\d*|\d)\.(?P<bugfix_wildcard>(?(minor_wildcard)\+|\+?))(?P<bugfix>[1-9]\d*|\d)'

wildcard_version_pattern = compile_regex(version_regex)

fixed_version_pattern = compile_regex(r'(?P<major>[1-9]\d*|\d)\.(?P<minor>[1-9]\d*|\d)\.(?P<bugfix>[1-9]\d*|\d)')

allowed_dependency_scopes = ['main', 'test']

import re


allowed_pralinefile_fields = ['artifact', 'organization', 'version', 'platforms', 'architectures', 'compilers', 'modes', 'dependencies']

allowed_pralinefile_dependency_fields = ['artifact', 'organization', 'scope', 'version']

allowed_architectures = ['arm', 'x32', 'x64']

allowed_platforms = ['windows', 'linux', 'darwin']

allowed_compilers = ['gcc', 'clang', 'msvc', 'clang_cl']

allowed_modes = ['debug', 'release']

allowed_dependency_scopes = ['main', 'test']

mandatory_fields = ['organization', 'artifact', 'version']

organization_regex = r"[a-z]+(?:_[a-z]+)*"

artifact_regex = r"[a-z]+(?:_[a-z]+)*"

fixed_version_regex = r"(?P<major>[1-9]\d*|[1-9])\.(?P<minor>[1-9]\d*|\d)\.(?P<bugfix>[1-9]\d*|\d)"

wildcard_version_regex = r"(?P<major>[1-9]\d*|[1-9])\.(?P<minor_wildcard>\+)?(?P<minor>[1-9]\d*|\d)\.(?P<bugfix_wildcard>(?(minor_wildcard)\+|\+?))(?P<bugfix>[1-9]\d*|\d)"

organization_pattern = re.compile(organization_regex)

artifact_pattern = re.compile(artifact_regex)

fixed_version_pattern = re.compile(fixed_version_regex)

wildcard_version_pattern = re.compile(wildcard_version_regex)

identifier_regex = (f"(?P<organization>{organization_regex})-"
                    f"(?P<artifact>{artifact_regex})-"
                    f"(?P<architecture>{'|'.join(allowed_architectures)})-"
                    f"(?P<platform>{'|'.join(allowed_platforms)})-"
                    f"(?P<compiler>{'|'.join(allowed_compilers)})-"
                    f"(?P<mode>{'|'.join(allowed_modes)})")

fixed_package_pattern = re.compile(f"{identifier_regex}-{fixed_version_regex}\\.tar\\.gz")

wildcard_package_pattern = re.compile(f"{identifier_regex}-{wildcard_version_regex}\\.tar\\.gz")

package_extension = '.tar.gz'

def get_artifact_full_name(organization, artifact, architecture, platform, compiler, mode, version):
    return f"{organization}-{artifact}-{architecture}-{platform}-{compiler}-{mode}-{version}"

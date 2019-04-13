from praline.client.project.pipeline.stage.base import stage
from praline.common.compiler.base import get_compilers
from praline.common.file_system import join, which
from praline.common.pralinefile import pralinefile_from_path
from praline.common.system_information import architecture, platform


@stage(produces=['pralinefile', 'architecture', 'platform', 'compiler'])
def scan_pralinefile(working_directory, data, cache, arguments):
    try:
        data['pralinefile'] = pralinefile = pralinefile_from_path(join(working_directory, 'Pralinefile'))
    except FileNotFoundError:
        raise RuntimeError(f"no Pralinefile was found in current working directory {working_directory}")

    if architecture not in pralinefile['architectures']:
        raise RuntimeError(f"{architecture} is not supported -- supported architectures are {pralinefile['architectures']}")
    data['architecture'] = architecture

    if platform not in pralinefile['platforms']:
        raise RuntimeError(f"{platform} is not supported -- supported architectures are {pralinefile['platforms']}")
    data['platform'] = platform

    available_compilers = [compiler for compiler in get_compilers() if which(compiler.executable()) is not None and platform in compiler.allowed_platforms()]
    compilers = [compiler for compiler in available_compilers if compiler.name() in pralinefile['compilers']]
    if not compilers:
        raise RuntimeError(f"no suitable compiler was found -- available compilers are {[c.name() for c in available_compilers]} while specified compilers are {pralinefile['compilers']}")
    data['compiler'] = compilers[0]

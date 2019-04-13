import requests
from praline.client.configuration import configuration
from praline.common.file_system import copyfileobj, basename
from praline.common.packaging import package_from_pralinefile, dependant_packages_from_pralinefile
from praline.common.tracing import trace

remote_repository = configuration['remote-repository'].rstrip('/')


@trace(remote_repository=remote_repository)
def pull_package(package_path):
    response = requests.get(f'{remote_repository}/package/{basename(package_path)}', stream=True)
    if response.status_code == 200:
        with open(package_path, 'wb') as f:
            copyfileobj(response.raw, f)
    else:
        raise RuntimeError(f'request failed with status code {response.status_code} - {response.text}')


@trace(remote_repository=remote_repository)
def push_package(package_path):
    package = basename(package_path)
    headers = {'Content-type': 'application/octet-stream', 'Slug': package}
    with open(package_path, 'rb') as f:
        response = requests.put(f'{remote_repository}/package/{package}', data=f, headers=headers)
    if response.status_code != 201:
        raise RuntimeError(f'request failed with status code {response.status_code} - {response.text}')


@trace(remote_repository=remote_repository)
def solve_dependencies(pralinefile, architecture, platform, compiler):
    dependencies = dependant_packages_from_pralinefile(pralinefile, architecture, platform, compiler)
    if not dependencies:
        return []

    payload = {
        'package': package_from_pralinefile(pralinefile, architecture, platform, compiler),
        'dependencies': dependencies
    }
    response = requests.get(f'{remote_repository}/solve-dependencies', json=payload)
    if response.status_code != 200:
        raise RuntimeError(f'request failed with status code {response.status_code} - {response.text}')
    return response.json()

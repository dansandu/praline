from praline.common.file_system import basename, FileSystem
from praline.common.package import get_package, get_package_dependencies_from_pralinefile
from praline.common.tracing import trace
from typing import Any, Dict
import requests


class RemoteProxy:
    def __init__(self, file_system: FileSystem, remote_repository: str):
        self.file_system       = file_system
        self.remote_repository = remote_repository.rstrip('/')

    def __repr__(self):
        return f'RemoteProxy({self.remote_repository})'

    @trace
    def pull_package(self, package_path: str) -> None:
        response = requests.get(f'{self.remote_repository}/package/{basename(package_path)}', stream=True)
        if response.status_code == 200:
            with self.file_system.open_file(package_path, 'wb') as package:
                self.file_system.copyfileobj(response.raw, package)
        else:
            raise RuntimeError(f"request failed with status code {response.status_code}: {response.text}")

    @trace
    def push_package(self, package_path: str) -> None:
        package = basename(package_path)
        headers = {'Content-type': 'application/octet-stream', 'Slug': package}
        with self.file_system.open_file(package_path, 'rb') as f:
            response = requests.put(f'{self.remote_repository}/package/{package}', data=f, headers=headers)
        if response.status_code != 201:
            raise RuntimeError(f"request failed with status code {response.status_code}: {response.text}")

    @trace
    def solve_dependencies(self, pralinefile: Dict[str, Any], architecture: str, platform: str, compiler: str, mode: str) -> Dict[str, str]:
        package_dependencies = get_package_dependencies_from_pralinefile(pralinefile, architecture, platform, compiler, mode)
        if not package_dependencies:
            return {}

        payload = {
            'package': get_package(pralinefile['organization'], pralinefile['artifact'], architecture, platform, compiler, mode, pralinefile['version']),
            'dependencies': package_dependencies
        }
        response = requests.get(f'{self.remote_repository}/solve-dependencies', json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"request failed with status code {response.status_code}: {response.text}")
        return response.json()

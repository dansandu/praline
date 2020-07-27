from praline.server.configuration import configuration
import logging.config

logging.config.dictConfig(configuration['logging'])

from flask import Flask, send_from_directory, request, Response, jsonify
from praline.common.file_system import FileSystem, join
from praline.common.hashing import hash_archive
from praline.common.package import get_package_dependencies_recursively
from typing import Dict


file_system = FileSystem()

server = Flask(__name__, root_path=file_system.get_working_directory())

repository_path = join(configuration['repository'], 'packages')


@server.route('/package/<package>', methods=['GET', 'PUT'])
def package(package) -> Response:
    file_system.create_directory_if_missing(repository_path)
    if request.method == 'GET':
        return send_from_directory(repository_path, package, as_attachment=True)
    elif request.method == 'PUT':
        package_path = join(repository_path, package)
        if file_system.exists(package_path):
            return Response(f"package '{package}' already exists -- increment the version and try again", status=409, mimetype='text/plain')
        with open(package_path, 'wb') as f:
            f.write(request.stream.read())
        return Response(f"succesfully created package '{package}'", status=201, mimetype='text/plain')


@server.route('/solve-dependencies', methods=['GET'])
def solve_dependencies() -> Dict[str, str]:
    file_system.create_directory_if_missing(repository_path)
    payload = request.get_json()
    try:
        dependencies = get_package_dependencies_recursively(file_system, payload['package'], payload['dependencies'], repository_path)
        dependencies_with_hashes = {d: hash_archive(file_system, join(repository_path, d)) for d in dependencies}
        return jsonify(dependencies_with_hashes)
    except RuntimeError as exception:
        return Response(str(exception), status=400, mimetype='text/plain')

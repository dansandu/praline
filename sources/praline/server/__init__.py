from flask import Flask, send_from_directory, request, Response, jsonify
from logging.config import dictConfig as configure_logging
from praline.common.file_system import join, exists, create_directory_if_missing, current_working_directory
from praline.server.configuration import configuration
from praline.server.package_dependency import get_dependant_packages_recursively

configure_logging(configuration['logging'])

server = Flask(__name__, root_path=current_working_directory())

package_directory = join(configuration['repository'], 'packages')


@server.route('/package/<package>', methods=['GET', 'PUT'])
def package(package):
    create_directory_if_missing(package_directory)
    if request.method == 'GET':
        return send_from_directory(package_directory, package, as_attachment=True)
    elif request.method == 'PUT':
        package_path = join(package_directory, package)
        if exists(package_path):
            return Response(f"package '{package}' already exists -- increment the version and try again", status=409, mimetype='text/plain')
        with open(package_path, 'wb') as f:
            f.write(request.stream.read())
        return Response(f"succesfully created package '{package}'", status=201, mimetype='text/plain')


@server.route('/solve-dependencies', methods=['GET'])
def solve_dependencies():
    create_directory_if_missing(package_directory)
    payload = request.get_json()
    try:
        return jsonify(get_dependant_packages_recursively(payload['package'], payload['dependencies'], package_directory))
    except RuntimeError as exception:
        return Response(str(exception), status=400, mimetype='text/plain')

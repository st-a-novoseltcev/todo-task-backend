from flask import Blueprint, request, make_response, jsonify
from flask_jwt_extended import jwt_required
from marshmallow.exceptions import ValidationError

from server.errors.exc import InvalidSchema
from server.file import service as file_service
from server.file.service import FileSchema


file_blueprint = Blueprint('file', __name__)
prefix = '/file/'


@file_blueprint.route(prefix + 'download', methods=['POST'])
@jwt_required()
def open_file():
    try:
        schema = FileSchema(only='id').load(request.json)
    except ValidationError as e:
        raise InvalidSchema(e.args[0])

    id = schema['id']
    file_data = file_service.download(id=id)
    return make_response(file_data)


@file_blueprint.route(prefix, methods=['POST'])
@jwt_required()
def create():
    try:
        file = request.files['file']
        request.json['name'] = file.filename
        request.json['data'] = file.read()
        schema = FileSchema(only=('name', 'task', 'data')).load(request.json)
    except ValueError or ValidationError as e:
        raise InvalidSchema(e.args[0])

    file_service.create(**schema)
    return jsonify(filename=schema['name']), 202


@file_blueprint.route(prefix, methods=['DELETE'])
@jwt_required()
def delete():
    try:
        schema = FileSchema(only='id').load(request.json)
    except ValidationError as e:
        raise InvalidSchema(e.args[0])

    id = schema['id']
    filename = file_service.delete(id)
    return jsonify(filename=filename), 202

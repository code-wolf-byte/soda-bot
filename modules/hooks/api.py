from flask import request, jsonify, Blueprint

hooks_blueprint = Blueprint('hooks', __name__, static_folder=None, template_folder=None)


@hooks_blueprint.route('/', methods=['POST', 'GET'])
def hooks():
    return jsonify({'message': 'Welcome to the index of the hooks API'})


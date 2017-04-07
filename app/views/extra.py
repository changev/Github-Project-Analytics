from flask import Flask,send_from_directory, Blueprint

extra=Blueprint('extra', __name__)

@extra.route('/favicon.ico', methods=['GET'])
def get_favicon_ico():
    return send_from_directory('static', 'img/favicon.ico')
    
from flask import Flask, request, jsonify

import crypto.rsa
from datastore import DataStore
from crypto.utils import RsaKeys

app = Flask(__name__)
db = DataStore()
pub, priv = crypto.rsa.generate_keypair(71, 101)
server_keys = RsaKeys(public=pub, private=priv)


@app.route('/')
def home():
    return "Hello, World!"


@app.route('/api/get_public_key', methods=['GET'])
def get_rsa_public_key():
    return jsonify({"message": "OK", "server_public_key": server_keys.public})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    client_public_key = data.get('public_key')
    username = crypto.rsa.decrypt(server_keys.private, data.get('username'))
    password = crypto.rsa.decrypt(server_keys.private, data.get('password'))
    if not db.validate_credentials(username, password):
        return jsonify(data={'message': 'Not registered'}), 401
    try:
        session_token = db.start_session(username, client_public_key)
    except ValueError as ex:
        return jsonify({'message': str(ex)}), 401
    response_data = {"message": "Authenticated", 'session_token': session_token}
    return jsonify(response_data)


@app.route('/api/get_file_content', methods=['GET'])
def get_file_content():
    data = request.get_json()

    session_token = crypto.rsa.decrypt(server_keys.private, data.get('session_token'))
    file_name = data.get('file_name')

    file_content = db.get_file_content(session_token=session_token, file_name=file_name)
    app.logger.debug(f"Requested: {file_name}, content: {file_content}")

    response = {
        "file_name": file_name,
        "file_content": file_content
    }
    return jsonify(response)


@app.route('/api/get_all_files', methods=['GET'])
def get_all_files():
    session_token = crypto.rsa.decrypt(server_keys.private, request.get_json().get('session_token'))
    response = {
        "all_files_names": db.get_all_files(session_token=session_token)
    }
    return jsonify(response)


@app.route('/api/new_file', methods=['POST'])
def load_file():
    data = request.get_json()

    session_token = crypto.rsa.decrypt(server_keys.private, data.get('session_token'))
    file_name = data.get('file_name')
    try:
        db.put_file(session_token=session_token, file_name=file_name, file_content='')
    except ValueError as ex:
        return jsonify({'message': str(ex)}), 401
    response = {
        "message": f"Posted {file_name}"
    }
    return jsonify(response)


@app.route('/api/edit_file', methods=['POST'])
def edit_file():
    data = request.get_json()
    session_token = crypto.rsa.decrypt(server_keys.private, data.get('session_token'))
    file_name = data.get('file_name')
    file_content = data.get('file_content')
    try:
        db.edit_file(session_token=session_token, file_name=file_name, new_file_content=file_content)
    except ValueError as ex:
        return jsonify({'message': str(ex)}), 401
    response = {
        "message": f"Edited {file_name}"
    }
    return jsonify(response)


@app.route('/api/delete_file', methods=['DELETE'])
def delete_file():
    data = request.get_json()
    session_token = crypto.rsa.decrypt(server_keys.private, data.get('session_token'))
    file_name = data.get('file_name')
    try:
        db.delete_file(session_token=session_token, file_name=file_name)
    except ValueError as ex:
        return jsonify({'message': str(ex)}), 401
    response = {
        "message": f"Deleted {file_name}"
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run()

from flask import Flask, request, jsonify

from datastore import DataStore

app = Flask(__name__)
db = DataStore()


@app.route('/')
def home():
    return "Hello, World!"


@app.route('/api/login', methods=['POST'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    e = int(request.args.get('pub_key_e'))
    p = int(request.args.get('pub_key_p'))
    if not db.validate_credentials(username, password):
        return jsonify(data={'message': 'Not registered'}), 401
    try:
        session_token = db.start_session(username, (e, p))
    except ValueError as ex:
        return jsonify({'message': str(ex)}), 401
    response_data = {"message": "Authenticated", 'session_token': session_token}
    return jsonify(response_data)


@app.route('/api/get_file_content', methods=['GET'])
def get_file_content():
    session_token = request.args.get('session_token')
    file_name = request.args.get('file_name')

    response = {
        "file_name": file_name,
        "file_content": db.get_file_content(session_token=session_token, file_name=file_name)
    }
    return jsonify(response)


@app.route('/api/get_all_files', methods=['GET'])
def get_all_files():
    session_token = request.args.get('session_token')
    response = {
        "all_files_names": db.get_all_files(session_token=session_token)
    }
    return jsonify(response)


@app.route('/api/load_file', methods=['POST'])
def load_file():
    session_token = request.args.get('session_token')
    file_name = request.args.get('file_name')
    file_content = request.args.get('file_content')
    try:
        db.put_file(session_token=session_token, file_name=file_name, file_content=file_content)
    except ValueError as ex:
        return jsonify({'message': str(ex)}), 401
    response = {
        "message": f"Posted {file_name}"
    }
    return jsonify(response)


@app.route('/api/edit_file', methods=['PATCH'])
def edit_file():
    session_token = request.args.get('session_token')
    file_name = request.args.get('file_name')
    file_content = request.args.get('new_file_content')
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
    session_token = request.args.get('session_token')
    file_name = request.args.get('file_name')
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

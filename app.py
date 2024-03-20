from typing import Tuple

from flask import Flask, jsonify, request, Response, json
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(data: dict = None, status: int = 200, message: str = "") -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world suka!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)


# TODO: Implement the rest of the API here!

@app.route("/users", methods=['GET'])
def users_get():
    team = request.args.get("team")
    all_users = db.get('users')
    if team:
        users_team = [user for user in all_users if user["team"] == team]
        return create_response(data={"users": users_team})
    return create_response(data={"users": all_users})


@app.route("/users", methods=['POST'])
def users_post():
    user_data = json.loads(request.data)
    if "name" not in user_data:
        return create_response(data={"content": f"Parameter 'name' is empty"}, status=422)
    if "age" not in user_data:
        return create_response(data={"content": f"Parameter 'age' is empty"}, status=422)
    if "team" not in user_data:
        return create_response(data={"content": f"Parameter 'team' is empty"}, status=422)
    user_created = db.create("users", user_data)
    return create_response({"content": f"User ({user_created}) was created!"})


@app.route("/users/<id>", methods=['GET'])
def user_create(id):
    user = db.getById('users', int(id))
    if user:
        return create_response(data={"user": user})
    else:
        return create_response(data={"content": f"No user with such id ({id})"}, status=404)

@app.route("/users/<id>", methods=['PUT'])
def user_update(id):
    user_data = json.loads(request.data)
    updated_user = db.updateById("users", int(id), user_data)
    if updated_user:
        return create_response(data={"content": f"User ({updated_user['name']}) fields ({user_data}) were updated!"})
    return create_response(data={"content": f"No user with such id ({id})"}, status=404)


@app.route("/users/<id>", methods=['DELETE'])
def user_delete(id):
    user_delete = db.getById("users", int(id))
    if user_delete:
        db.deleteById("users", int(id))
        return create_response({"content": f"User ({user_delete}) was deleted!"})
    return create_response(data={"content": f"No user with such id ({id})"}, status=404)



"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)

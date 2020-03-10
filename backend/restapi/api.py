from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask_pymongo import PyMongo
import bcrypt
import jwt
import datetime
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['TOKEN_SECRET_KEY'] = 'alecisgod'
app.config['MONGO_DBNAME'] = 'MLAI'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MLAI'

mongodb = PyMongo(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers['Token']

        if not token:
            return jsonify({'message': 'Token is missing !'}), 403

        try: 
            data = jwt.decode(token, app.config['TOKEN_SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid'}), 403
        
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def hello():
    return jsonify({"about": "hello world"})

@app.route("/login", methods=['POST'])
def login():     
    username = request.get_json()['username']
    password = request.get_json()['password']

    users = mongodb.db.users
    if users.find_one({'username': username, 'password': password}):
        
        # generate token
        token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['TOKEN_SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return jsonify({'error':'Could not verify!', 'WWW-Authenticate': 'Basic realm="Login Required"'}), 401

@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        users = mongodb.db.users

        username = request.get_json()['username']
        password = request.get_json()['password']
        firstname = request.get_json()['firstname']
        lastname = request.get_json()['lastname']

        
        existing_user = users.find_one({'username':  username})

        if existing_user is None:
            users.insert({
                'username': username,
                'password': password,
                'firstname': firstname,
                'lastname': lastname
            })
            return jsonify({'message':'sign up sucessfully'})

        return jsonify({'error': 'username existed'}), 422
    else:
        return''


@app.route("/userinfo", methods=['GET'])
def user():     
    username = request.get_json()['username']

    users = mongodb.db.users
    user = users.find_one({'username': username})        
    print(str(user))


@app.route('/protected', methods=['POST'])
@token_required
def protected():
    return jsonify({'message': 'with token'})


if __name__ == '__main__':
    app.run(debug=True)
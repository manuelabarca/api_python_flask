"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Post, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/post', methods=['POST'])
def create_post():
    body = request.get_json()
    if body is None:
        return {"error": "The body is null or undefined"}, 400
    
    user = User.get_user(body['email'])
    user_id = user.id

    Post.create_post(user_id, body['description'])
    
    return {"message": "post created"}, 200

@app.route('/post', methods=['GET'])
def get_all_post():
    posts = Post.get_all_post()

    return jsonify(posts), 200


@app.route('/favorite', methods=['POST'])
def create_favorite():
    body = request.get_json()
    if body is None:
        return {"error": "Body is empty or null"}, 400
    
    user = User.get_user(body['email'])
    user_id = user.id

    owner_post = User.get_user(body['owner_email_post'])
    owner_id = owner_post.id

    post = Post.get_post(owner_id)
    post_id = post.id

    Favorite.create_favorite(user_id, post_id)

    return {"message": "Favorite created OK"}, 200

@app.route('/favorite', methods=['GET'])
def get_all_favorites():
    favorites = Favorite.get_all_favorites()
    return jsonify(favorites), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

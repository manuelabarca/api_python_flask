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
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup the Flask-JWT-Extended extension / Configuración JWT TOKEN en donde este 'app'
app.config["JWT_SECRET_KEY"] = "paralelepipedo"  # Change this!
jwt = JWTManager(app)

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
@jwt_required()
def create_post():
    body = request.get_json()
    if body is None:
        return {"error": "The body is null or undefined"}, 400

    user_id = get_jwt_identity()
    Post.create_post(user_id, body['description'])
    
    return {"message": "post created"}, 200

@app.route('/post/', methods=['GET'])
@jwt_required()
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

    if "owner_email_post" in body:
        owner_post = User.get_user(body['owner_email_post'])
        owner_id = owner_post.id

        post = Post.get_post(owner_id)
        post_id = post.id

        Favorite.create_favorite(user_id, post_id, None)

        return {"message": "Post agregado a favoritos "}, 200


    if "planet_id" in body:

        Favorite.create_favorite(user_id, None, body['planet_id'])
        return {"message": "Planeta agregado a favoritos"}, 200



@app.route('/favorite', methods=['GET'])
def get_all_favorites():
    favorites = Favorite.get_all_favorites()
    return jsonify(favorites), 200

@app.route('/favorite/<int:user_id>', methods=['GET'])
def get_favorites_by_id(user_id):
    favorites = Favorite.get_favorites_by_id(user_id)
    return jsonify(favorites), 200



@app.route('/login', methods=['POST'])
def sign_in():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email, password=password).first()
    if User is None:
        return jsonify({"msg": "Email or password is wrong"}), 401
    
    token = create_access_token(identity=user.id)
    return jsonify({"token": token}), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

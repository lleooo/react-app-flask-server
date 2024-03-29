from functools import wraps

from flask import request, jsonify, make_response
from app.api import api_bp as api
from app.database import mongo_client
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity
from jwt.exceptions import ExpiredSignatureError
from jwt import decode


def check(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except ExpiredSignatureError as e:
            return jsonify({'msg': 'access expired'}), 401
        except Exception as e:
            print(e)
            return jsonify({'msg': 'Internal server error'}), 500

        return fn(*args, **kwargs)
    return decorator


@api.route('/verify-token', methods=["GET"])
@check
def verify():
    return jsonify({'msg': 'Token is valid'}), 200


@api.route('/login', methods=["POST"])
def login():
    col = mongo_client.client['db_create_by_leo']['collection_create_by_leo']

    email = request.json.get('email')
    password = request.json.get('password')

    dbquery = {
        "email": email,
        'password': password
    }

    mydoc = list(col.find(dbquery))

    if len(mydoc) == 0:
        return {"msg": "Wrong email or password"}, 401

    response = jsonify({"msg": "successful", "data": {
        'id': str(mydoc[0]['_id']),
        'username': mydoc[0]['username'],
        'email': mydoc[0]['email'],
        'favorite': mydoc[0]['favorite']
    }})

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response


@api.route('/signup', methods=["POST"])
def signup():
    col = mongo_client.client['db_create_by_leo']['collection_create_by_leo']

    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    dbquery = {
        "username": username,
        'password': password
    }

    mydoc = col.find(dbquery)

    if len(list(mydoc)) != 0:
        return jsonify({'msg': 'user exist'}), 409

    col.insert_one({
        "username": username,
        "email": email,
        "password": password,
        'favorite': []
    })

    return jsonify({'message': 'success'}), 201


@api.route('/logout', methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@api.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@api.route('/addFavorite', methods=['POST'])
@check
def get_favorite():
    col = mongo_client.client['db_create_by_leo']['collection_create_by_leo']

    current_user_email = get_jwt_identity()
    movieID = request.json.get('movieID')

    existing_favorite = col.find_one({"email": current_user_email, "favorite": {"$in": [movieID]}})

    if existing_favorite:
        return jsonify({"message": "Favorite already exists"}), 400

    col.update_one(
        {"email": current_user_email},
        {"$push": {"favorite": movieID}}
    )

    favoriteMovies = col.find_one({"email": current_user_email})['favorite']

    response = jsonify({"msg": "successful", "data": favoriteMovies})

    return response, 200


@api.route('/removeFavorite', methods=['DELETE'])
@check
def rm_favorite():
    try:
        col = mongo_client.client['db_create_by_leo']['collection_create_by_leo']

        movieID = request.json.get('movieID')
        current_user_email = get_jwt_identity()

        result = col.update_one(
            {"email": current_user_email},
            {"$pull": {"favorite": movieID}}
        )

        favoriteMovies = col.find_one({"email": current_user_email})['favorite']
        if result.modified_count == 1:
            return jsonify({"msg": "success", "data": favoriteMovies}), 200
        else:
            return jsonify({"msg": "error"}), 404

    except Exception as e:
        return jsonify({"msg": str(e)}), 500

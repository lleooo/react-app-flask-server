from flask import request, jsonify
from app.api import api_bp as api
from app.database import mongo_client
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt_identity

from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_AUTH_CLINT_ID = "54532982628-dmk3e53gfh1djcel7htm5pkiq3h85u9g.apps.googleusercontent.com"


@api.route("/verify-token", methods=["GET"])
@jwt_required()
def verify():
    return jsonify({"msg": "Token is valid"}), 200


@api.route("/login", methods=["POST"])
def login():
    col = mongo_client.client["db_create_by_leo"]["collection_create_by_leo"]

    email = request.json.get("email")
    password = request.json.get("password")

    dbquery = {"email": email, "password": password}

    mydoc = list(col.find(dbquery))

    if len(mydoc) == 0:
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    response = jsonify(
        {
            "msg": "successful",
            "data": {
                "id": str(mydoc[0]["_id"]),
                "username": mydoc[0]["username"],
                "email": mydoc[0]["email"],
                "favorite": mydoc[0]["favorite"],
                'access_token': access_token,
                'refresh_token': refresh_token
            },
        }
    )

    return response, 200


@api.route("/signup", methods=["POST"])
def signup():
    col = mongo_client.client["db_create_by_leo"]["collection_create_by_leo"]

    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")

    dbquery = {"username": username, "password": password}

    mydoc = col.find(dbquery)

    if len(list(mydoc)) != 0:
        return jsonify({"msg": "user exist"}), 409

    col.insert_one(
        {"username": username, "email": email, "password": password, "favorite": []}
    )

    return jsonify({"msg": "success"}), 201


@api.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"refresh": True, 'access_token': access_token}), 200


@api.route("/googleSignIn", methods=["POST"])
def google_sign_in():
    col = mongo_client.client["db_create_by_leo"]["collection_create_by_leo"]
    token = request.json['credential']

    # verify token first
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_AUTH_CLINT_ID
        )

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return jsonify({"error": "Wrong issuer"}), 400
    except ValueError as e:
        return jsonify({"error": "Invalid token"}), 400

    user = col.find_one({"username": id_info['name'], "email": id_info['email']})

    if not user:
        user_data = {
            "username": id_info['name'],
            "email": id_info['email'],
            "password": '',
            "favorite": []
        }
        col.insert_one(user_data)

    else:
        user_data = user

    access_token = create_access_token(identity=id_info['email'])
    refresh_token = create_refresh_token(identity=id_info['email'])

    response_data = jsonify({
        "msg": "successful",
        "data": {
            "username": user_data["username"],
            "email": user_data["email"],
            "favorite": user_data["favorite"]
        },
        'access_token': access_token,
        'refresh_token': refresh_token,
    })

    return response_data, 200


@ api.route("/addFavorite", methods=["POST"])
@ jwt_required()
def get_favorite():
    col = mongo_client.client["db_create_by_leo"]["collection_create_by_leo"]

    current_user_email = get_jwt_identity()
    movieID = request.json.get("movieID")

    existing_favorite = col.find_one(
        {"email": current_user_email, "favorite": {"$in": [movieID]}}
    )

    if existing_favorite:
        return jsonify({"msg": "Favorite already exists"}), 400

    col.update_one({"email": current_user_email}, {"$push": {"favorite": movieID}})

    favoriteMovies = col.find_one({"email": current_user_email})["favorite"]

    response = jsonify({"msg": "successful", "data": favoriteMovies})

    return response, 200


@ api.route("/removeFavorite", methods=["DELETE"])
@ jwt_required()
def rm_favorite():
    try:
        col = mongo_client.client["db_create_by_leo"]["collection_create_by_leo"]
        print(col)
        movieID = request.json.get("movieID")
        print(movieID)
        current_user_email = get_jwt_identity()
        print(current_user_email)
        result = col.update_one(
            {"email": current_user_email}, {"$pull": {"favorite": movieID}}
        )
        print(result)
        favoriteMovies = col.find_one({"email": current_user_email})["favorite"]
        if result.modified_count == 1:
            return jsonify({"msg": "success", "data": favoriteMovies}), 200
        else:
            return jsonify({"msg": "error"}), 404

    except Exception as e:
        return jsonify({"msg": str(e)}), 500


# @api.route("/test", methods=["POST"])
# @jwt_required()
# def test():
#     return "hi"


# @api.route("/test_ref", methods=["POST"])
# @jwt_required(refresh=True)
# def test_ref():
#     identity = get_jwt_identity()
#     access_token = create_access_token(identity=identity)
#     return jsonify(access_token=access_token)

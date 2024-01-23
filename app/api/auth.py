from flask import request,jsonify,make_response
from app.api import api_bp as api
from flask_jwt_extended import create_access_token,unset_jwt_cookies,jwt_required,get_jwt_identity,set_access_cookies


@api.route('/login', methods=["POST"])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if username != 'test' or password!='test' :
        return  {"msg": "Wrong email or password"}, 401
    
    response = jsonify({"msg": "login successful"})
    
    access_token = create_access_token(identity=username)

    set_access_cookies(response, access_token)

    return response

@api.route('/logout', methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@api.route('/refresh', methods=['POST'])
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200

@api.route('/getlove')
@jwt_required()
def getlove():
    return '123'

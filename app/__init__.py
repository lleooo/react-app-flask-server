import os

from flask import Flask
from datetime import timedelta

from app.api import api_bp
from app.database import mongo_client
from flask_jwt_extended import JWTManager
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        JWT_SECRET_KEY="dev",
        JWT_TOKEN_LOCATION="cookies",
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=60),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
        JWT_COOKIE_SECURE=True,  # 在生產環境中設置為 True
        JWT_COOKIE_SAMESITE='None',
        # JWT_COOKIE_DOMAIN='.netlify.app',

        MONGO_URI='mongodb+srv://test:test@cluster0.iu7brvi.mongodb.net/?retryWrites=true&w=majority'
        # DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    jwt = JWTManager(app)
    mongo_client.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")
    CORS(app, supports_credentials=True)

    return app

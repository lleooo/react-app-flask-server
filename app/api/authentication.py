from app.api import api_bp as api


@api.route("/reg")
def register():
    return "hello register"

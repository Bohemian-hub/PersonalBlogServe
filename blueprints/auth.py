from flask import Blueprint, request, jsonify
from service import authenticate_user  # 导入 service 模块

# 创建一个蓝图对象，设置/auth 为蓝图的前缀
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# test hello word!
@auth_bp.route("/hello")
def hello():
    return jsonify({
        "error": 0,
        "body": "Hello, World!",
        "msg": ""
    })


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": 400,
            "body": None,
            "msg": "Username and password are required"
        }), 400

    try:
        user = authenticate_user(username, password)
        if user:
            return jsonify({
                "error": 0,
                "body": {
                    "user": {
                        "id": user["id"],
                        "username": user["username"],
                        "auth": user["auth"],
                    }
                },
                "msg": "Login successful"
            })
        else:
            return jsonify({
                "error": 401,
                "body": None,
                "msg": "Invalid username or password"
            }), 401
    except Exception as e:
        return jsonify({
            "error": 500,
            "body": None,
            "msg": str(e)
        }), 500
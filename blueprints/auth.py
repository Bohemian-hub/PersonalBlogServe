from flask import Blueprint, request, jsonify
from services.auth import (
    authenticate_user,
    create_user,
    verify_email_exists,
    generate_token,
    save_user_token,
)
from mail import send_email
import random
import re
import redis

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


@auth_bp.route("/send-code", methods=["POST"])
def send_verification_code():
    data = request.json
    email = data.get("email")

    if not email or not is_valid_email(email):
        return jsonify({"error": 400, "body": None, "msg": "请输入有效的邮箱地址"}), 200

    if verify_email_exists(email):
        return jsonify({"error": 400, "body": None, "msg": "该邮箱已被注册"}), 200

    code = "".join(random.choices("0123456789", k=6))

    if send_email(email, code):
        redis_client.setex(f"verify_code:{email}", 300, code)
        return jsonify({"error": 0, "body": None, "msg": "验证码已发送"}), 200
    else:
        return jsonify({"error": 500, "body": None, "msg": "验证码发送失败 form backon"}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    code = data.get("code")
    username = data.get("username")
    password = data.get("password")

    if not all([email, code, username, password]):
        return jsonify({"error": 400, "body": None, "msg": "请填写所有必填字段"}), 200

    if not is_valid_email(email):
        return jsonify({"error": 400, "body": None, "msg": "邮箱格式不正确"}), 200

    stored_code = redis_client.get(f"verify_code:{email}")
    if not stored_code or stored_code != code:
        return jsonify({"error": 400, "body": None, "msg": "验证码无效或已过期"}), 200

    try:
        user = create_user(email, username, password)
        redis_client.delete(f"verify_code:{email}")
        return (
            jsonify(
                {
                    "error": 0,
                    "body": {
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "username": user["username"],
                        }
                    },
                    "msg": "注册成功",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": 500, "body": None, "msg": str(e)}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": 400, "body": None, "msg": "请输入邮箱和密码"}), 200

    try:
        user = authenticate_user(email, password)
        if user:
            # 生成新的token
            token = generate_token(user["id"])
            # 保存token到数据库
            save_user_token(user["id"], token)

            return (
                jsonify(
                    {
                        "error": 0,
                        "body": {
                            "user": {
                                "id": user["id"],
                                "email": user["email"],
                                "username": user["username"],
                                "auth": user["auth"],
                            },
                            "token": token,
                        },
                        "msg": "登录成功",
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": 401, "body": None, "msg": "邮箱或密码错误"}), 200
    except Exception as e:
        return jsonify({"error": 500, "body": None, "msg": str(e)}), 200

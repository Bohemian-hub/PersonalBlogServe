from functools import wraps
from flask import request, jsonify
from services.auth import verify_token


def require_auth(f):
    """需要登录认证的装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token or token == "default_token":
            return jsonify({"error": 401, "body": None, "msg": "请先登录"}), 401

        try:
            user = verify_token(token)
            if not user:
                return (
                    jsonify(
                        {"error": 401, "body": None, "msg": "token无效，请重新登录"}
                    ),
                    401,
                )

            # 将用户信息添加到request对象中，供后续使用
            request.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return (
                jsonify({"error": 500, "body": None, "msg": f"认证失败: {str(e)}"}),
                500,
            )

    return decorated_function


def require_admin(f):
    """需要管理员权限的装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token or token == "default_token":
            return jsonify({"error": 401, "body": None, "msg": "请先登录"}), 401

        try:
            user = verify_token(token)
            if not user:
                return (
                    jsonify(
                        {"error": 401, "body": None, "msg": "token无效，请重新登录"}
                    ),
                    401,
                )

            if user.get("auth") != "1":
                return jsonify({"error": 403, "body": None, "msg": "无权限访问"}), 403

            request.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return (
                jsonify({"error": 500, "body": None, "msg": f"认证失败: {str(e)}"}),
                500,
            )

    return decorated_function

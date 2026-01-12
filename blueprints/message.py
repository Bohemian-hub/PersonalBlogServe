from flask import Blueprint, request, jsonify
from services.message import get_messages, create_message, delete_message

message_bp = Blueprint("message", __name__, url_prefix="/message")


@message_bp.route("/list", methods=["GET"])
def list_messages():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    # Public endpoint only shows public messages
    messages, total, error = get_messages(page, limit, include_private=False)
    if error:
        return jsonify({"error": 500, "msg": error}), 500
    return (
        jsonify(
            {"error": 0, "body": {"list": messages, "total": total}, "msg": "success"}
        ),
        200,
    )


@message_bp.route("/admin/list", methods=["GET"])
def list_all_messages():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    # Admin endpoint shows all messages
    messages, total, error = get_messages(page, limit, include_private=True)
    if error:
        return jsonify({"error": 500, "msg": error}), 500
    return (
        jsonify(
            {"error": 0, "body": {"list": messages, "total": total}, "msg": "success"}
        ),
        200,
    )


@message_bp.route("/add", methods=["POST"])
def add_message():
    data = request.json
    if not data or not data.get("content"):
        return jsonify({"error": 400, "msg": "Content is required"}), 400

    success, error = create_message(data)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "Message posted successfully"}), 200


@message_bp.route("/delete", methods=["POST"])
def remove_message():
    data = request.json
    msg_id = data.get("id")
    if not msg_id:
        return jsonify({"error": 400, "msg": "ID is required"}), 400

    success, error = delete_message(msg_id)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "Deleted successfully"}), 200

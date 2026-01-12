from flask import Blueprint, request, jsonify
from services.friend_link import (
    get_friend_links,
    create_friend_link,
    update_friend_link,
    delete_friend_link,
    get_friend_link_requests,
    create_friend_link_request,
    approve_friend_link_request,
    reject_friend_link_request,
)

friend_link_bp = Blueprint("friend_link", __name__, url_prefix="/friend_link")


@friend_link_bp.route("/list", methods=["GET"])
def list_links():
    links, error = get_friend_links()
    if error:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "body": links, "msg": "success"}), 200


@friend_link_bp.route("/create", methods=["POST"])
def create_link():
    data = request.json
    if not data or not data.get("name") or not data.get("url"):
        return jsonify({"error": 400, "msg": "Name and URL are required"}), 400

    success, error = create_friend_link(data)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "created successfully"}), 200


@friend_link_bp.route("/update", methods=["POST"])
def update_link():
    data = request.json
    link_id = data.get("id")
    if not link_id:
        return jsonify({"error": 400, "msg": "ID is required"}), 400

    success, error = update_friend_link(link_id, data)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "updated successfully"}), 200


@friend_link_bp.route("/delete", methods=["POST"])
def delete_link():
    data = request.json
    link_id = data.get("id")
    if not link_id:
        return jsonify({"error": 400, "msg": "ID is required"}), 400

    success, error = delete_friend_link(link_id)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "deleted successfully"}), 200


# Request endpoints
@friend_link_bp.route("/request/list", methods=["GET"])
def list_requests():
    reqs, error = get_friend_link_requests()
    if error:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "body": reqs, "msg": "success"}), 200


@friend_link_bp.route("/request/create", methods=["POST"])
def create_request_endpoint():
    data = request.json
    if not data or not data.get("name") or not data.get("url"):
        return jsonify({"error": 400, "msg": "Name and URL are required"}), 400

    success, error = create_friend_link_request(data)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "application submitted successfully"}), 200


@friend_link_bp.route("/request/approve", methods=["POST"])
def approve_request_endpoint():
    data = request.json
    req_id = data.get("id")
    if not req_id:
        return jsonify({"error": 400, "msg": "ID is required"}), 400

    success, error = approve_friend_link_request(req_id)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "approved successfully"}), 200


@friend_link_bp.route("/request/reject", methods=["POST"])
def reject_request_endpoint():
    data = request.json
    req_id = data.get("id")
    if not req_id:
        return jsonify({"error": 400, "msg": "ID is required"}), 400

    success, error = reject_friend_link_request(req_id)
    if not success:
        return jsonify({"error": 500, "msg": error}), 500
    return jsonify({"error": 0, "msg": "rejected successfully"}), 200

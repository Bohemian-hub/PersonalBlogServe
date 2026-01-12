from flask import Blueprint, request, jsonify
from services.activity import get_activities, upsert_activity

activity_bp = Blueprint("activity", __name__, url_prefix="/activity")


@activity_bp.route("/list", methods=["GET"])
def get_activity_list():
    page = int(
        request.args.get("page", 1)
    )  # Currently not fully implementing pagination in service, but good to have params prepared
    limit = int(request.args.get("limit", 100))  # Default limit to reasonable amount

    # Can add start_date/end_date params from request

    result, error = get_activities(limit=limit)

    if error:
        return jsonify({"error": 500, "msg": f"Failed to get activities: {error}"}), 500

    return jsonify({"error": 0, "body": result, "msg": "Success"}), 200


# Endpoint to add/update activity (Optional for now as user asked for 'presentation', but needed for 'convenience')
@activity_bp.route("/upload", methods=["POST"])
def upload_activity():
    if not request.is_json:
        return jsonify({"error": 400, "msg": "JSON required"}), 400

    data = request.json
    if not data.get("date") or not data.get("mood"):
        return jsonify({"error": 400, "msg": "Date and Mood are required"}), 400

    success, error = upsert_activity(data)

    if error:
        return jsonify({"error": 500, "msg": f"Failed: {error}"}), 500

    return jsonify({"error": 0, "msg": "Activity saved"}), 200


@activity_bp.route("/submit_from_email", methods=["POST"])
def submit_from_email():
    # Handle form submission from email
    data = {}
    if request.is_json:
        data = request.json
    else:
        # Handling form-data (application/x-www-form-urlencoded)
        data = request.form.to_dict()

    if not data.get("date") or not data.get("mood"):
        return (
            """
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h2 style="color: red;">Submission Failed</h2>
            <p>Date and Mood are required.</p>
        </div>
        """,
            400,
        )

    success, error = upsert_activity(data)

    if error:
        return (
            f"""
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h2 style="color: red;">Error</h2>
            <p>{error}</p>
        </div>
        """,
            500,
        )

    return (
        """
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1 style="color: #4a90e2;">Update Successful!</h1>
        <p>Your daily activity has been recorded.</p>
        <p>Mood: {}</p>
        <p>Date: {}</p>
        <script>setTimeout(function(){{window.close();}}, 3000);</script>
    </div>
    """.format(
            data.get("mood"), data.get("date")
        ),
        200,
    )

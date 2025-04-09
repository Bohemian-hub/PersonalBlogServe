from flask import Blueprint, request, jsonify
from services.article import create_article

article_bp = Blueprint("article", __name__, url_prefix="/article")


@article_bp.route("/upload", methods=["POST"])
def upload_article():
    """
    上传文章接口
    """
    if not request.is_json:
        return jsonify({"error": 400, "body": None, "msg": "请发送JSON格式的请求"}), 400

    article_data = request.json

    # 必要字段验证
    required_fields = ["title", "content_url"]
    for field in required_fields:
        if field not in article_data:
            return (
                jsonify({"error": 400, "body": None, "msg": f"缺少必要字段: {field}"}),
                400,
            )

    # 创建文章
    article, error = create_article(article_data)

    if error:
        return (
            jsonify({"error": 500, "body": None, "msg": f"创建文章失败: {error}"}),
            500,
        )

    # 返回创建的文章信息 - article现在是字典而不是对象
    return jsonify({"error": 0, "body": article, "msg": "文章创建成功"}), 200

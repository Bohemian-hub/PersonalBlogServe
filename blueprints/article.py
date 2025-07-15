from flask import Blueprint, request, jsonify
import traceback
from services.article import (
    create_article,
    get_articles,
    delete_article,
    publish_draft_article,
    get_article_by_id,
)

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


@article_bp.route("/list", methods=["GET"])
def get_article_list():
    """
    获取文章列表接口 - 支持分页和筛选
    """
    try:
        # 获取查询参数
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        keyword = request.args.get("keyword", "").strip()
        category = request.args.get("category", "").strip()
        status = request.args.get("status", "").strip()

        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        # 处理空字符串
        keyword = keyword if keyword else None
        category = category if category else None
        status = status if status else None

        # 获取文章列表
        result, error = get_articles(
            page=page,
            page_size=page_size,
            keyword=keyword,
            category=category,
            status=status,
        )

        if error:
            # 打印详细错误信息用于调试
            print(f"获取文章列表错误: {error}")
            return (
                jsonify(
                    {"error": 500, "body": None, "msg": f"获取文章列表失败: {error}"}
                ),
                500,
            )

        return jsonify({"error": 0, "body": result, "msg": "获取成功"}), 200

    except ValueError as e:
        print(f"参数错误: {str(e)}")
        return (
            jsonify({"error": 400, "body": None, "msg": "页码或页面大小参数无效"}),
            400,
        )
    except Exception as e:
        # 打印完整的错误堆栈
        print(f"服务器错误: {str(e)}")
        print(traceback.format_exc())
        return (
            jsonify({"error": 500, "body": None, "msg": f"服务器错误: {str(e)}"}),
            500,
        )


@article_bp.route("/<int:article_id>", methods=["DELETE"])
def delete_article_by_id(article_id):
    """
    删除文章接口
    """
    try:
        success, error = delete_article(article_id)

        if error:
            return (
                jsonify({"error": 500, "body": None, "msg": f"删除失败: {error}"}),
                500,
            )

        return jsonify({"error": 0, "body": None, "msg": "删除成功"}), 200

    except Exception as e:
        return (
            jsonify({"error": 500, "body": None, "msg": f"服务器错误: {str(e)}"}),
            500,
        )


@article_bp.route("/<int:article_id>/publish", methods=["PATCH"])
def publish_draft(article_id):
    """
    发布草稿文章接口
    """
    try:
        article, error = publish_draft_article(article_id)

        if error:
            return (
                jsonify({"error": 500, "body": None, "msg": f"发布失败: {error}"}),
                500,
            )

        return jsonify({"error": 0, "body": article, "msg": "发布成功"}), 200

    except Exception as e:
        return (
            jsonify({"error": 500, "body": None, "msg": f"服务器错误: {str(e)}"}),
            500,
        )


@article_bp.route("/<int:article_id>", methods=["GET"])
def get_article_detail(article_id):
    """
    获取单篇文章详情接口
    """
    try:
        article, error = get_article_by_id(article_id)

        if error:
            return (
                jsonify({"error": 500, "body": None, "msg": f"获取失败: {error}"}),
                500,
            )

        if not article:
            return jsonify({"error": 404, "body": None, "msg": "文章不存在"}), 404

        return jsonify({"error": 0, "body": article, "msg": "获取成功"}), 200

    except Exception as e:
        return (
            jsonify({"error": 500, "body": None, "msg": f"服务器错误: {str(e)}"}),
            500,
        )

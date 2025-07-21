from flask import Blueprint, request, jsonify, send_file
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
import datetime
from services.media import save_media_info, get_media_info, read_markdown_content
from middlewares.auth import require_admin

# 加载环境变量
load_dotenv()

# 获取媒体存储路径
IMAGE_STORAGE_PATH = os.getenv("IMAGE_STORAGE_PATH")
MD_STORAGE_PATH = os.getenv("MD_STORAGE_PATH")

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# 允许的 Markdown 文件扩展名
ALLOWED_MD_EXTENSIONS = {"md", "markdown"}

media_bp = Blueprint("media", __name__, url_prefix="/media")


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_md_file(filename):
    """检查是否是允许的 Markdown 文件"""
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_MD_EXTENSIONS
    )


# 需要管理员权限的接口
@media_bp.route("/upload/image", methods=["POST"])
@require_admin
def upload_image():
    # 检查是否有文件部分
    if "file" not in request.files:
        return jsonify({"error": 400, "body": None, "msg": "请选择文件"}), 200

    file = request.files["file"]

    # 如果用户未选择文件，浏览器也可能提交一个没有文件名的空部分
    if file.filename == "":
        return jsonify({"error": 400, "body": None, "msg": "未选择文件"}), 200

    if file and allowed_file(file.filename):
        # 安全地获取文件名
        filename = secure_filename(file.filename)
        # 创建唯一的文件名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # 创建基于日期的子目录
        today = datetime.datetime.now().strftime("%Y%m%d")
        upload_folder = os.path.join(IMAGE_STORAGE_PATH, today)

        # 确保存储目录存在
        os.makedirs(upload_folder, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        try:
            # 存储相对路径而非绝对路径
            relative_path = os.path.join(today, unique_filename)
            file_type = "image"
            media_id = save_media_info(relative_path, filename, file_type)

            # 构建访问URL
            media_url = f"/media/image/{media_id}"

            return (
                jsonify(
                    {
                        "error": 0,
                        "body": {"id": media_id, "url": media_url},
                        "msg": "上传成功",
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"error": 500, "body": None, "msg": str(e)}), 200

    return jsonify({"error": 400, "body": None, "msg": "不支持的文件类型"}), 200


@media_bp.route("/upload/markdown", methods=["POST"])
@require_admin
def upload_markdown():
    # 检查是否有文件部分
    if "file" not in request.files:
        return jsonify({"error": 400, "body": None, "msg": "请选择文件"}), 200

    file = request.files["file"]

    # 检查标题是否存在
    title = request.form.get("title")
    if not title:
        return jsonify({"error": 400, "body": None, "msg": "请提供标题"}), 200

    # 可选描述
    description = request.form.get("description", "")

    # 如果用户未选择文件，浏览器也可能提交一个没有文件名的空部分
    if file.filename == "":
        return jsonify({"error": 400, "body": None, "msg": "未选择文件"}), 200

    if file and allowed_md_file(file.filename):
        # 安全地获取文件名
        filename = secure_filename(file.filename)
        # 创建唯一的文件名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # 创建基于日期的子目录
        today = datetime.datetime.now().strftime("%Y%m%d")
        upload_folder = os.path.join(MD_STORAGE_PATH, today)

        # 确保存储目录存在
        os.makedirs(upload_folder, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        try:
            # 存储相对路径而非绝对路径
            relative_path = os.path.join(today, unique_filename)
            file_type = "markdown"
            md_id = save_media_info(relative_path, filename, file_type)

            # 构建访问URL
            md_url = f"/media/markdown/{md_id}"

            return (
                jsonify(
                    {
                        "error": 0,
                        "body": {
                            "id": md_id,
                            "url": md_url,
                            "title": title,
                            "description": description,
                        },
                        "msg": "上传成功",
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"error": 500, "body": None, "msg": str(e)}), 200

    return jsonify({"error": 400, "body": None, "msg": "不支持的文件类型"}), 200


# 公开接口（不需要认证）
@media_bp.route("/image/<image_id>", methods=["GET"])
def get_media(image_id):
    try:
        # 从数据库获取媒体信息
        media = get_media_info(image_id)

        if not media:
            return jsonify({"error": 404, "body": None, "msg": "媒体不存在"}), 200

        # 获取完整文件路径
        file_path = os.path.join(IMAGE_STORAGE_PATH, media["relative_path"])

        # 返回文件
        return send_file(file_path, mimetype=f"image/{media['file_type']}")

    except Exception as e:
        return jsonify({"error": 500, "body": None, "msg": str(e)}), 200


@media_bp.route("/markdown/<md_id>", methods=["GET"])
def get_markdown(md_id):
    try:
        # 从数据库获取 Markdown 文件信息
        md_file = get_media_info(md_id)

        if not md_file:
            return (
                jsonify({"error": 404, "body": None, "msg": "Markdown 文件不存在"}),
                200,
            )

        # 获取完整文件路径
        file_path = os.path.join(MD_STORAGE_PATH, md_file["relative_path"])

        # 读取文件内容
        content = read_markdown_content(file_path)

        # 返回 Markdown 内容和元数据
        return (
            jsonify(
                {
                    "error": 0,
                    "body": {
                        "id": md_id,
                        "content": content,
                        "original_filename": md_file["original_filename"],
                    },
                    "msg": "获取成功",
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": 500, "body": None, "msg": str(e)}), 200

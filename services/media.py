import uuid
from database import connect_to_database
from mysql.connector import Error


def save_media_info(relative_path, original_filename, file_type):
    """将媒体信息保存到数据库"""
    connection = connect_to_database()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor(dictionary=True)
        media_id = str(uuid.uuid4())
        query = "INSERT INTO media (id, relative_path, original_filename, file_type) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (media_id, relative_path, original_filename, file_type))
        connection.commit()
        cursor.close()
        connection.close()
        return media_id
    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        raise Exception(str(e))


def get_media_info(media_id):
    """从数据库获取媒体信息"""
    connection = connect_to_database()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM media WHERE id = %s"
        cursor.execute(query, (media_id,))
        media = cursor.fetchone()
        cursor.close()
        connection.close()
        return media
    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        raise Exception(str(e))


def read_markdown_content(file_path):
    """读取 Markdown 文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except Exception as e:
        raise Exception(f"读取 Markdown 文件失败: {str(e)}")

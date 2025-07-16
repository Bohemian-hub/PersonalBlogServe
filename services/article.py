from mysql.connector import Error
from database import connect_to_database
from datetime import datetime


def create_article(article_data):
    """
    创建一篇新文章

    Args:
        article_data (dict): 包含文章信息的字典

    Returns:
        tuple: (成功创建的文章对象或None, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return None, "数据库连接失败"

    try:
        cursor = connection.cursor(dictionary=True)

        # 处理标签 - 确保它们是字符串格式
        tags = article_data.get("tags", "")
        if isinstance(tags, list):
            tags = ",".join(tags)

        # 准备插入数据
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        insert_query = """
        INSERT INTO articles (
            title, summary, cover_image_url, category, tags, 
            likes_count, comments_count,views_count, created_at, content_url, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)
        """

        values = (
            article_data.get("title"),
            article_data.get("summary"),
            article_data.get("cover_image_url"),
            article_data.get("category"),
            tags,
            article_data.get("likes_count", 0),
            article_data.get("comments_count", 0),
            article_data.get("views_count", 0),
            current_time,
            article_data.get("content_url"),
            article_data.get("status", "draft"),
        )

        cursor.execute(insert_query, values)
        connection.commit()

        # 获取创建的文章
        article_id = cursor.lastrowid
        query = "SELECT * FROM articles WHERE id = %s"
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()

        cursor.close()
        connection.close()

        # 处理标签格式用于返回
        if article and article.get("tags"):
            article["tags"] = article["tags"].split(",") if article["tags"] else []

        return article, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return None, str(e)


def get_articles(page=1, page_size=10, keyword=None, category=None, status=None):
    """
    分页获取文章列表

    Args:
        page (int): 页码，从1开始
        page_size (int): 每页文章数量
        keyword (str): 搜索关键词
        category (str): 文章分类
        status (str): 文章状态

    Returns:
        tuple: (文章列表和总数的字典或None, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return None, "数据库连接失败"

    try:
        cursor = connection.cursor(dictionary=True)

        # 构建查询条件
        where_conditions = []
        params = []

        if keyword:
            where_conditions.append("title LIKE %s")
            params.append(f"%{keyword}%")

        if category:
            where_conditions.append("category = %s")
            params.append(category)

        if status:
            where_conditions.append("status = %s")
            params.append(status)

        where_clause = (
            " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        )

        # 查询总数
        count_query = f"SELECT COUNT(*) as total FROM articles{where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # 分页查询文章列表 - 修正字段名，返回views而不是views_count
        offset = (page - 1) * page_size
        list_query = f"""
        SELECT id, title, summary, cover_image_url, category, tags, 
               likes_count, comments_count, 
               COALESCE(views_count, 0) as views,
               created_at, status 
        FROM articles{where_clause} 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        cursor.execute(list_query, params + [page_size, offset])
        articles = cursor.fetchall()

        cursor.close()
        connection.close()

        # 处理数据格式
        for article in articles:
            # 处理标签格式
            if article.get("tags"):
                article["tags"] = article["tags"].split(",") if article["tags"] else []
            else:
                article["tags"] = []

            # 确保views字段存在且为数字
            if article.get("views") is None:
                article["views"] = 0

            # 格式化创建时间
            if article.get("created_at"):
                if isinstance(article["created_at"], str):
                    # 如果已经是字符串格式，保持不变
                    pass
                else:
                    # 如果是datetime对象，转换为字符串
                    article["created_at"] = article["created_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

        return {
            "items": articles,
            "total": total,
            "page": page,
            "page_size": page_size,
        }, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return None, str(e)
    except Exception as e:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        return None, f"查询出错: {str(e)}"


def delete_article(article_id):
    """
    删除文章

    Args:
        article_id (int): 文章ID

    Returns:
        tuple: (成功标志, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return False, "数据库连接失败"

    try:
        cursor = connection.cursor()

        # 检查文章是否存在
        check_query = "SELECT id FROM articles WHERE id = %s"
        cursor.execute(check_query, (article_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "文章不存在"

        # 删除文章
        delete_query = "DELETE FROM articles WHERE id = %s"
        cursor.execute(delete_query, (article_id,))
        connection.commit()

        cursor.close()
        connection.close()

        return True, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return False, str(e)


def publish_draft_article(article_id):
    """
    发布草稿文章

    Args:
        article_id (int): 文章ID

    Returns:
        tuple: (更新后的文章或None, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return None, "数据库连接失败"

    try:
        cursor = connection.cursor(dictionary=True)

        # 检查文章是否存在且为草稿状态
        check_query = "SELECT * FROM articles WHERE id = %s AND status = 'draft'"
        cursor.execute(check_query, (article_id,))
        article = cursor.fetchone()

        if not article:
            cursor.close()
            connection.close()
            return None, "文章不存在或不是草稿状态"

        # 更新文章状态为已发布
        update_query = "UPDATE articles SET status = 'published' WHERE id = %s"
        cursor.execute(update_query, (article_id,))
        connection.commit()

        # 获取更新后的文章
        cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        updated_article = cursor.fetchone()

        cursor.close()
        connection.close()

        # 处理标签格式
        if updated_article and updated_article.get("tags"):
            updated_article["tags"] = (
                updated_article["tags"].split(",") if updated_article["tags"] else []
            )

        return updated_article, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return None, str(e)


def get_article_by_id(article_id):
    """
    根据ID获取单篇文章

    Args:
        article_id (int): 文章ID

    Returns:
        tuple: (文章对象或None, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return None, "数据库连接失败"

    try:
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM articles WHERE id = %s"
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()

        cursor.close()
        connection.close()

        if article and article.get("tags"):
            article["tags"] = article["tags"].split(",") if article["tags"] else []

        return article, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return None, str(e)


def update_article(article_id, article_data):
    """
    更新文章

    Args:
        article_id (int): 文章ID
        article_data (dict): 包含文章信息的字典

    Returns:
        tuple: (更新后的文章对象或None, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return None, "数据库连接失败"

    try:
        cursor = connection.cursor(dictionary=True)

        # 检查文章是否存在
        check_query = "SELECT id FROM articles WHERE id = %s"
        cursor.execute(check_query, (article_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return None, "文章不存在"

        # 处理标签 - 确保它们是字符串格式
        tags = article_data.get("tags", "")
        if isinstance(tags, list):
            tags = ",".join(tags)

        # 准备更新数据
        update_fields = []
        values = []

        # 动态构建更新字段
        if "title" in article_data:
            update_fields.append("title = %s")
            values.append(article_data["title"])

        if "summary" in article_data:
            update_fields.append("summary = %s")
            values.append(article_data["summary"])

        if "cover_image_url" in article_data:
            update_fields.append("cover_image_url = %s")
            values.append(article_data["cover_image_url"])

        if "category" in article_data:
            update_fields.append("category = %s")
            values.append(article_data["category"])

        if "tags" in article_data:
            update_fields.append("tags = %s")
            values.append(tags)

        if "content_url" in article_data:
            update_fields.append("content_url = %s")
            values.append(article_data["content_url"])

        if "status" in article_data:
            update_fields.append("status = %s")
            values.append(article_data["status"])

        if not update_fields:
            cursor.close()
            connection.close()
            return None, "没有需要更新的字段"

        # 执行更新
        update_query = f"UPDATE articles SET {', '.join(update_fields)} WHERE id = %s"
        values.append(article_id)

        cursor.execute(update_query, values)
        connection.commit()

        # 获取更新后的文章
        query = "SELECT * FROM articles WHERE id = %s"
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()

        cursor.close()
        connection.close()

        # 处理标签格式用于返回
        if article and article.get("tags"):
            article["tags"] = article["tags"].split(",") if article["tags"] else []

        return article, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return None, str(e)


def get_article_content(article_id):
    """
    获取文章完整内容（包括Markdown内容）

    Args:
        article_id (int): 文章ID

    Returns:
        tuple: (文章对象或None, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return None, "数据库连接失败"

    try:
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM articles WHERE id = %s"
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()

        cursor.close()
        connection.close()

        if not article:
            return None, "文章不存在"

        # 处理标签格式
        if article.get("tags"):
            article["tags"] = article["tags"].split(",") if article["tags"] else []
        else:
            article["tags"] = []

        # 确保所有必要字段都存在
        required_fields = [
            "title",
            "summary",
            "cover_image_url",
            "category",
            "content_url",
            "status",
        ]
        for field in required_fields:
            if field not in article or article[field] is None:
                article[field] = ""

        # 格式化创建时间
        if article.get("created_at") and hasattr(article["created_at"], "strftime"):
            article["created_at"] = article["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        print(f"获取文章数据成功: {article}")  # 添加调试日志
        return article, None

    except Error as e:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        print(f"数据库错误: {str(e)}")  # 添加调试日志
        return None, str(e)
    except Exception as e:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        print(f"获取文章内容异常: {str(e)}")  # 添加调试日志
        return None, str(e)


def unpublish_published_article(article_id):
    """
    撤回已发布文章为草稿

    Args:
        article_id (int): 文章ID

    Returns:
        tuple: (更新后的文章或None, 错误信息或None)
    """
    connection = connect_to_database()
    if not connection:
        return None, "数据库连接失败"

    try:
        cursor = connection.cursor(dictionary=True)

        # 检查文章是否存在且为已发布状态
        check_query = "SELECT * FROM articles WHERE id = %s AND status = 'published'"
        cursor.execute(check_query, (article_id,))
        article = cursor.fetchone()

        if not article:
            cursor.close()
            connection.close()
            return None, "文章不存在或不是已发布状态"

        # 更新文章状态为草稿
        update_query = "UPDATE articles SET status = 'draft' WHERE id = %s"
        cursor.execute(update_query, (article_id,))
        connection.commit()

        # 获取更新后的文章
        cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        updated_article = cursor.fetchone()

        cursor.close()
        connection.close()

        # 处理标签格式
        if updated_article and updated_article.get("tags"):
            updated_article["tags"] = (
                updated_article["tags"].split(",") if updated_article["tags"] else []
            )

        return updated_article, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return None, str(e)


def batch_delete_articles_service(article_ids):
    """
    批量删除文章（只能删除草稿状态的文章）

    Args:
        article_ids (list): 文章ID列表

    Returns:
        tuple: (成功删除数量, 失败数量, 错误信息)
    """
    connection = connect_to_database()
    if not connection:
        return 0, len(article_ids), "数据库连接失败"

    success_count = 0
    error_count = 0
    error_messages = []

    try:
        cursor = connection.cursor(dictionary=True)

        for article_id in article_ids:
            try:
                # 检查文章是否存在且为草稿状态
                check_query = "SELECT id, status FROM articles WHERE id = %s"
                cursor.execute(check_query, (article_id,))
                article = cursor.fetchone()

                if not article:
                    error_count += 1
                    error_messages.append(f"文章ID {article_id} 不存在")
                    continue

                if article["status"] != "draft":
                    error_count += 1
                    error_messages.append(f"文章ID {article_id} 不是草稿状态，无法删除")
                    continue

                # 删除文章
                delete_query = "DELETE FROM articles WHERE id = %s"
                cursor.execute(delete_query, (article_id,))
                success_count += 1

            except Exception as e:
                error_count += 1
                error_messages.append(f"删除文章ID {article_id} 失败: {str(e)}")

        connection.commit()
        cursor.close()
        connection.close()

        error_msg = "; ".join(error_messages[:3])  # 只显示前3个错误
        if len(error_messages) > 3:
            error_msg += f" 等{len(error_messages)}个错误"

        return success_count, error_count, error_msg

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return 0, len(article_ids), str(e)


def batch_publish_articles_service(article_ids):
    """
    批量发布文章（只能发布草稿状态的文章）

    Args:
        article_ids (list): 文章ID列表

    Returns:
        tuple: (成功发布数量, 失败数量, 错误信息)
    """
    connection = connect_to_database()
    if not connection:
        return 0, len(article_ids), "数据库连接失败"

    success_count = 0
    error_count = 0
    error_messages = []

    try:
        cursor = connection.cursor(dictionary=True)

        for article_id in article_ids:
            try:
                # 检查文章是否存在且为草稿状态
                check_query = (
                    "SELECT id, status FROM articles WHERE id = %s AND status = 'draft'"
                )
                cursor.execute(check_query, (article_id,))
                article = cursor.fetchone()

                if not article:
                    error_count += 1
                    error_messages.append(f"文章ID {article_id} 不存在或不是草稿状态")
                    continue

                # 更新文章状态为已发布
                update_query = "UPDATE articles SET status = 'published' WHERE id = %s"
                cursor.execute(update_query, (article_id,))
                success_count += 1

            except Exception as e:
                error_count += 1
                error_messages.append(f"发布文章ID {article_id} 失败: {str(e)}")

        connection.commit()
        cursor.close()
        connection.close()

        error_msg = "; ".join(error_messages[:3])  # 只显示前3个错误
        if len(error_messages) > 3:
            error_msg += f" 等{len(error_messages)}个错误"

        return success_count, error_count, error_msg

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return 0, len(article_ids), str(e)


def batch_unpublish_articles_service(article_ids):
    """
    批量撤回文章（只能撤回已发布状态的文章）

    Args:
        article_ids (list): 文章ID列表

    Returns:
        tuple: (成功撤回数量, 失败数量, 错误信息)
    """
    connection = connect_to_database()
    if not connection:
        return 0, len(article_ids), "数据库连接失败"

    success_count = 0
    error_count = 0
    error_messages = []

    try:
        cursor = connection.cursor(dictionary=True)

        for article_id in article_ids:
            try:
                # 检查文章是否存在且为已发布状态
                check_query = "SELECT id, status FROM articles WHERE id = %s AND status = 'published'"
                cursor.execute(check_query, (article_id,))
                article = cursor.fetchone()

                if not article:
                    error_count += 1
                    error_messages.append(f"文章ID {article_id} 不存在或不是已发布状态")
                    continue

                # 更新文章状态为草稿
                update_query = "UPDATE articles SET status = 'draft' WHERE id = %s"
                cursor.execute(update_query, (article_id,))
                success_count += 1

            except Exception as e:
                error_count += 1
                error_messages.append(f"撤回文章ID {article_id} 失败: {str(e)}")

        connection.commit()
        cursor.close()
        connection.close()

        error_msg = "; ".join(error_messages[:3])  # 只显示前3个错误
        if len(error_messages) > 3:
            error_msg += f" 等{len(error_messages)}个错误"

        return success_count, error_count, error_msg

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return 0, len(article_ids), str(e)

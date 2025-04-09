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
            likes_count, comments_count, created_at, content_url, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            article_data.get("title"),
            article_data.get("summary"),
            article_data.get("cover_image_url"),
            article_data.get("category"),
            tags,
            article_data.get("likes_count", 0),
            article_data.get("comments_count", 0),
            current_time,
            article_data.get("content_url"),
            article_data.get("status", "draft")
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

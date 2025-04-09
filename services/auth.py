from mysql.connector import Error
from database import connect_to_database

def authenticate_user(email, password):
    """验证用户登录"""
    connection = connect_to_database()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    except Error as e:
        raise Exception(str(e))

def verify_email_exists(email):
    """检查邮箱是否已存在"""
    connection = connect_to_database()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id FROM user WHERE email = %s"
        cursor.execute(query, (email,))
        exists = cursor.fetchone() is not None
        cursor.close()
        connection.close()
        return exists
    except Error as e:
        raise Exception(str(e))

def create_user(email, username, password):
    """创建新用户"""
    connection = connect_to_database()
    if not connection:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO user (email, username, password, auth) VALUES (%s, %s, %s, '0')"
        cursor.execute(query, (email, username, password))
        connection.commit()
        
        # 获取新创建的用户信息
        user_id = cursor.lastrowid
        query = "SELECT * FROM user WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        return user
    except Error as e:
        raise Exception(str(e))
from mysql.connector import Error
from database import connect_to_database

def authenticate_user(username, password):
    """查询指定用户名和密码的用户信息"""
    connection = connect_to_database()
    if not connection:
        raise Exception("Database connection failed")
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    except Error as e:
        raise Exception(str(e))
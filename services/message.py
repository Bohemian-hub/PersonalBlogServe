from database import connect_to_database
from datetime import datetime


def get_messages(page=1, limit=10, include_private=False):
    conn = connect_to_database()
    if not conn:
        return [], 0, "Database connection failed"

    try:
        cursor = conn.cursor(dictionary=True)
        offset = (page - 1) * limit

        # Build query based on visibility
        where_clause = ""
        params = []
        if not include_private:
            where_clause = "WHERE is_private = 0"

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM messages {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()["total"]

        # Get messages
        query = f"SELECT * FROM messages {where_clause} ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, params)
        result = cursor.fetchall()

        return result, total_count, None
    except Exception as e:
        return [], 0, str(e)
    finally:
        conn.close()


def create_message(data):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO messages (author, avatar, content, is_private, email)
            VALUES (%s, %s, %s, %s, %s)
        """
        is_private = 1 if data.get("isPrivate") else 0
        values = (
            data.get("author", "访客"),
            data.get("avatar", ""),
            data.get("content"),
            is_private,
            data.get("email", ""),
        )
        cursor.execute(query, values)
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_message(message_id):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"

    try:
        cursor = conn.cursor()
        query = "DELETE FROM messages WHERE id = %s"
        cursor.execute(query, (message_id,))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

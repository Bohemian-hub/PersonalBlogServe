from database import connect_to_database
import datetime


def get_friend_links():
    conn = connect_to_database()
    if not conn:
        return [], "Database connection failed"

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM friend_links ORDER BY created_at ASC"
        cursor.execute(query)
        result = cursor.fetchall()
        return result, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def create_friend_link(data):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO friend_links (name, description, url, logo, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            data.get("name"),
            data.get("description"),
            data.get("url"),
            data.get("logo"),
            data.get("status", "approved"),
        )
        cursor.execute(query, values)
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def update_friend_link(link_id, data):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"

    try:
        cursor = conn.cursor()
        query = """
            UPDATE friend_links 
            SET name=%s, description=%s, url=%s, logo=%s, status=%s
            WHERE id=%s
        """
        values = (
            data.get("name"),
            data.get("description"),
            data.get("url"),
            data.get("logo"),
            data.get("status", "approved"),
            link_id,
        )
        cursor.execute(query, values)
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_friend_link(link_id):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"

    try:
        cursor = conn.cursor()
        query = "DELETE FROM friend_links WHERE id = %s"
        cursor.execute(query, (link_id,))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_friend_link_requests():
    conn = connect_to_database()
    if not conn:
        return [], "Database connection failed"

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM friend_link_requests ORDER BY created_at ASC"
        cursor.execute(query)
        result = cursor.fetchall()
        return result, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def create_friend_link_request(data):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO friend_link_requests (name, description, url, logo, email, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("name"),
            data.get("description"),
            data.get("url"),
            data.get("logo"),
            data.get("email"),
            "pending",
        )
        cursor.execute(query, values)
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def approve_friend_link_request(request_id):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"

    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)

        # 1. Get request data
        cursor.execute(
            "SELECT * FROM friend_link_requests WHERE id = %s", (request_id,)
        )
        req = cursor.fetchone()
        if not req:
            raise Exception("Request not found")

        # 2. Insert into friend_links
        insert_query = """
            INSERT INTO friend_links (name, description, url, logo, status)
            VALUES (%s, %s, %s, %s, 'approved')
        """
        insert_values = (req["name"], req["description"], req["url"], req["logo"])
        cursor.execute(insert_query, insert_values)

        # 3. Update request status
        update_query = (
            "UPDATE friend_link_requests SET status = 'approved' WHERE id = %s"
        )
        cursor.execute(update_query, (request_id,))

        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def reject_friend_link_request(request_id):
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"
    try:
        cursor = conn.cursor()
        query = "UPDATE friend_link_requests SET status = 'rejected' WHERE id = %s"
        cursor.execute(query, (request_id,))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

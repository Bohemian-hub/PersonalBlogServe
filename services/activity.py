from mysql.connector import Error
from database import connect_to_database
from datetime import datetime


def get_activities(start_date=None, end_date=None, limit=None):
    """
    Get activities from the database.
    """
    connection = connect_to_database()
    if not connection:
        return None, "Database connection failed"

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM daily_activities"
        params = []
        conditions = []

        if start_date:
            conditions.append("date >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("date <= %s")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date DESC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cursor.execute(query, tuple(params))
        activities = cursor.fetchall()

        # Format dates as strings
        for activity in activities:
            if activity["date"]:
                activity["date"] = activity["date"].strftime("%Y-%m-%d")
            if activity["created_at"]:
                activity["created_at"] = activity["created_at"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            if activity["updated_at"]:
                activity["updated_at"] = activity["updated_at"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        cursor.close()
        connection.close()
        return activities, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return None, str(e)


def upsert_activity(activity_data):
    """
    Insert or update an activity.
    """
    connection = connect_to_database()
    if not connection:
        return None, "Database connection failed"

    try:
        cursor = connection.cursor(dictionary=True)

        insert_query = """
        INSERT INTO daily_activities (date, mood, description)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE mood = VALUES(mood), description = VALUES(description)
        """

        values = (
            activity_data.get("date"),
            activity_data.get("mood"),
            activity_data.get("description", ""),
        )

        cursor.execute(insert_query, values)
        connection.commit()

        cursor.close()
        connection.close()
        return True, None

    except Error as e:
        if connection.is_connected():
            cursor.close()
            connection.close()
        return False, str(e)

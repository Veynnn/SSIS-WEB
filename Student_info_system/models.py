import mysql.connector
from config import Config

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

# Execute query to modify data
def execute_query(query, data=None):
    db = get_db_connection()
    cursor = db.cursor()
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()
    return True

# Fetch data from the database
def fetch_query(query, data=None):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

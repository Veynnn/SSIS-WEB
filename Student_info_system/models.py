import mysql.connector
from config import DB_HOST,DB_NAME,DB_PASSWORD,DB_USER


print(f"{DB_HOST=}")
print(f"{DB_USER=}")
print(f"{DB_PASSWORD=}")
print(f"{DB_NAME=}")
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
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

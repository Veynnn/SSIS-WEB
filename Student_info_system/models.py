import mysql.connector
from config import Config

db = mysql.connector.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)


#-----------------------note: to execute sql query to modify data
def execute_query(query, data=None):
    cursor = db.cursor()
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    db.commit()
    cursor.close()
    return True

#------------------------note: dis fetch data 
def fetch_query(query, data=None):
    cursor = db.cursor(dictionary=True)
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

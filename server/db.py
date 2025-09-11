import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
def get_connection():
    try:
        con = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        return con
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def get_cursor():
    con = get_db_connection()
    if con:
        return con.cursor(dictionary=True)
    return None
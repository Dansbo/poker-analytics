import config
import mysql.connector

def connect_to_db():
    try:
        db = mysql.connector.connect(**config.DB_CONFIG)
        print("Connected")
        return db
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    connection = connect_to_db()
    if connection and connection.is_connected():
        print("Connection is active - Closing connection...")
        connection.close()
        print("MariaDB connection is closed")
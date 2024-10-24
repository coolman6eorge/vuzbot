from config import HOST, DATABASE, USER, PASSWORD
import mysql
import mysql.connector

try:
    connection = mysql.connector.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )
    if connection.is_connected():
        print("Connected to MySQL database")
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    connection = None

async def create_user(t_uid, nickname):
    """Insert a new user into the users table."""
    if connection is None:
        print("No connection to the database.")
        return
    query = """
    INSERT INTO users (t_uid, nickname)
    VALUES (%s, %s)
    """
    values = (t_uid, nickname)
    
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        print(f"User {nickname} created successfully.")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        cursor.close()

async def get_user_by_tid(t_uid):
    """Fetch user details by user_id."""
    if connection is None:
        print("No connection to the database.")
        return
    query = "SELECT * FROM users WHERE t_uid = %s"
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, (t_uid,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"Error fetching user: {e}")
    finally:
        cursor.close()

async def update_user_balance(t_uid, amount):
    """Update the balance of a user by user_id."""
    if connection is None:
        print("No connection to the database.")
        return
    query = "UPDATE users SET balance = balance + %s WHERE t_uid = %s"
    values = (amount, t_uid)
    
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        print(f"User {t_uid} balance updated by {amount}.")
    except Exception as e:
        print(f"Error updating balance: {e}")
    finally:
        cursor.close()

def close_connection(self):
    """Close the database connection."""
    if self.connection and self.connection.is_connected():
        self.connection.close()
        print("MySQL connection closed.")
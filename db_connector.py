import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#db creation
db = None

try:

  if db:
    print("Connected to MySQL database")

  else:
    # Configure MySQL Database Connection
    db = mysql.connector.connect(
    host="db-aws-mysql-clothing.cfs4282w8b6r.eu-north-1.rds.amazonaws.com",
    user="admin",
    password = os.getenv("AWSSQLPWD"), # Get the password from the environment variable
    database="clothing-store"
    )
  
except mysql.connector.Error as err:
  print(f"Error: {err}")
    

def dbtester():
  if db.is_connected():
    return True
  else: 
    return False
 

def validate_login(username, password):
  if db.is_connected():
    cursor = db.cursor()
    query = "SELECT * FROM login WHERE login_username = %s AND login_password = %s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    cursor.close()
    return result is not None
  else:
    return None
  
def register_user(first, last, username, password):
  if db.is_connected():
    cursor = db.cursor()
    # Check if the username already exists
    '''query = "SELECT * FROM login WHERE login_username = %s"
    cursor.execute(query, (username,))
    if cursor.fetchone() is not None:
      cursor.close()
      return False'''
    query = "INSERT INTO login (login_first_name, login_last_name, login_username, login_password, login_role) VALUES (%s, %s, %s, %s, 'customer')"
    cursor.execute(query, (first, last, username, password))
    db.commit()
    cursor.close()
    return True
  else:
    return False

    
        
          

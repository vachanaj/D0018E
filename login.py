import db_connector

db = db_connector.db

'''
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
'''


def validate_login(username, password):
    #print(f"Attempting login: {username}, {password}")  # Debugging
    if db.is_connected():
        cursor = db.cursor(dictionary=True)  # Return results as a dictionary
        query = "SELECT login_username, login_role FROM login WHERE login_username = %s AND login_password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        return user  # Return user details instead of just True/False
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

def register_admin(first, last, username, password):
  if db.is_connected():
    cursor = db.cursor()
    '''query = "SELECT * FROM login WHERE login_username = %s"
    cursor.execute(query, (username,))
    if cursor.fetchone() is not None:
      cursor.close()
      return False'''
    query = "INSERT INTO login (login_first_name, login_last_name, login_username, login_password, login_role) VALUES (%s, %s, %s, %s, 'admin')"
    cursor.execute(query, (first, last, username, password))
    db.commit()
    cursor.close()
    return True
  else:
    return False
  
def get_login_id(username):
  if db.is_connected():
    cursor = db.cursor()
    query = "SELECT * FROM login WHERE login_username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    return user
import db_connector

db = db_connector.db

def create_cart(user_id):
    if db.is_connected():
        cursor = db.cursor()
        query = "INSERT INTO cart (cart_login_id) VALUES (%s)"
        user_id = user_id[0]  
        cursor.execute(query, (user_id,))
        db.commit()
        cursor.close()
        print("Cart created")
        return True
    else:
        return False
    
def get_cart_id(user_id):
    if db.is_connected():
        try:
            cursor = db.cursor()
            query = "SELECT cart_id FROM cart WHERE cart_login_id = %s AND cart_id = (SELECT MAX(cart_id) FROM cart WHERE cart_login_id = %s)"
            user_id = user_id[0] 
            cursor.execute(query, (user_id, user_id))
            cart_id = cursor.fetchone()
            cursor.close()
            print("get_cart_id: ", cart_id)
            return cart_id
        except:
            return None
        
    else:
        return None

def delete_cart(cart_id):
    if db.is_connected():
        try:
            cursor = db.cursor()
            query = "DELETE FROM cart WHERE cart_id = %s"
            cart_id = cart_id[0] 
            cursor.execute(query, (cart_id,))
            db.commit()
            cursor.close()
            print("Cart deleted")
            return True
        except:
            return False
    else:
        return False
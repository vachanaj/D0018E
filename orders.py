import db_connector

db = db_connector.db

def create_order(user_id, total_price, timestamp):
    if db.is_connected():
        cursor = db.cursor()
        query = "INSERT INTO orders (orders_login_id, order_total_price, order_status, order_timestamp) VALUES (%s, %s, %s, %s)"
        user_id = user_id[0]
        cart_id = cart_id[0]
        cursor.execute(query, (user_id, total_price, 'Pending', timestamp))
        db.commit()
        cursor.close()
        print("Order created")
        return True
    else:
        return False
    
def get_order_id(user_id):
    if db.is_connected():
        try:
            cursor = db.cursor()
            query = "SELECT order_id FROM orders WHERE orders_login_id = %s AND order_id = (SELECT MAX(order_id) FROM orders WHERE orders_login_id = %s)"
            user_id = user_id[0]
            cursor.execute(query, (user_id, user_id))
            order_id = cursor.fetchone()
            cursor.close()
            print("get_order_id: ", order_id)
            return order_id
        except:
            return None
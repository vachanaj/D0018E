import db_connector

db = db_connector.db

def create_order(user_id, total_price, timestamp):
    if db.is_connected():
        print("Order creation started")
        cursor = db.cursor()
        query = "INSERT INTO orders (order_login_id, order_total_price, order_status, order_timestamp) VALUES (%s, %s, %s, %s)"
        user_id = user_id[0]
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
            query = "SELECT order_id FROM orders WHERE order_login_id = %s AND order_id = (SELECT MAX(order_id) FROM orders WHERE order_login_id = %s)"
            user_id = user_id[0]
            cursor.execute(query, (user_id, user_id))
            order_id = cursor.fetchone()
            cursor.close()
            #print("get_order_id: ", order_id)
            return order_id
        except:
            return None
        
def get_order_ids(user_id):
    if db.is_connected():
        try:
            cursor = db.cursor()
            #query = "SELECT order_id FROM orders WHERE order_login_id = %s AND order_id = (SELECT MAX(order_id) FROM orders WHERE order_login_id = %s)"
            query = "SELECT * FROM orders WHERE order_login_id = %s"
            user_id = user_id[0]
            cursor.execute(query, (user_id,))
            order_ids = cursor.fetchall()
            #for order_id in order_ids:
                #print("get_order_id: ", order_id[0])
            cursor.close()
            
            return order_ids
        except:
            return None
        
def get_all_orders():
    if db.is_connected():
        cursor = db.cursor()
        query = "SELECT * FROM orders"
        cursor.execute(query)
        orders = cursor.fetchall()
        cursor.close()
        return orders
    
    else:
        return False
    
def change_order_status(order_id):
    if db.is_connected():
        try:
            cursor = db.cursor()
            query = "UPDATE orders SET order_status = 'Delivered' WHERE order_id = %s"
            cursor.execute(query, (order_id,))
            db.commit()
            cursor.close()
            return True
        except:
            return False
    else:
        return False
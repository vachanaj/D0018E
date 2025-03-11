import db_connector

db = db_connector.db

def get_all_order_items():
    if db.is_connected():
        cursor = db.cursor()
        cursor.execute("SELECT * FROM order_items")
        order_items = cursor.fetchall()
        cursor.close()
        return order_items
    else:
        return None
    
def get_order_item(order_id):
    if db.is_connected():
        cursor = db.cursor()
        query = "SELECT * FROM order_items WHERE order_items_order_id = %s"
        cursor.execute(query, (order_id,))
        order_item = cursor.fetchone()
        cursor.close()
        return order_item
    else:   
        return None 

def add_order_item(order_id, asset_id, quantity, price):
    if db.is_connected():
        cursor = db.cursor()
        check_query = "SELECT order_items_quantity FROM order_items WHERE order_items_orders_id = %s AND order_items_assets_id = %s"
        cursor.execute(check_query, (order_id, asset_id))
        result = cursor.fetchone()
        
        if result:
            new_quantity = result[0] + quantity
            update_query = "UPDATE order_items SET order_items_assets_quantity = %s WHERE order_items_orders_id = %s AND order_items_assets_id = %s"
            cursor.execute(update_query, (new_quantity, order_id, asset_id))
        else:
            insert_query = "INSERT INTO order_items (order_items_orders_id, order_items_assets_id, order_items_assets_quantity) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (order_id, asset_id, quantity, price))
        db.commit()
        cursor.close()
        return True
    else:
        return False
    
def get_order_items(order_id):
    if db.is_connected():
        cursor = db.cursor(dictionary=True)
        query = '''
            SELECT assets_id, assets_type, assets_description, assets_price, assets_quantity, assets_img_name, order_items_quantity
            FROM order_items
            JOIN new_assets ON order_items.order_items_assets_id = assets.assets_id
            WHERE order_items_order_id = %s
        '''
        cursor.execute(query, (order_id,))
        order_items = cursor.fetchall()
        cursor.close()
        return order_items
    else:
        return None 
    
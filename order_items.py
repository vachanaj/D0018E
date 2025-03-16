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
        check_query = "SELECT order_items_assets_quantity FROM order_items WHERE order_items_orders_id = %s AND order_items_assets_id = %s"
        order_id = order_id[0]
        price = price[0]
        print("price: ", price)
        print("order_id: ", order_id)
        print("asset_id: ", asset_id)
        print("quantity: ", quantity)
        cursor.execute(check_query, (order_id, asset_id))
        result = cursor.fetchone()
        
        if result:
            print("result: ", result)
            new_quantity = result[0] + quantity
            update_query = "UPDATE order_items SET order_items_assets_quantity = %s WHERE order_items_orders_id = %s AND order_items_assets_id = %s"
            cursor.execute(update_query, (new_quantity, order_id, asset_id))

        else:
            print("result: ", result)
            insert_query = "INSERT INTO order_items (order_items_orders_id, order_items_assets_id, order_items_assets_quantity, order_items_quantity_price) VALUES (%s, %s, %s, %s)"
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
            SELECT assets_id, assets_type, assets_desc, assets_price, assets_quantity, assets_img_name, order_items_orders_id, order_items_assets_quantity
            FROM order_items
            JOIN assets ON order_items.order_items_assets_id = assets.assets_id
            WHERE order_items_orders_id = %s
        '''
        cursor.execute(query, (order_id,))
        order_items = cursor.fetchall()
        for item in order_items:
            print("item in items: ", item)
        cursor.close()
        return order_items
    else:
        return None 
    
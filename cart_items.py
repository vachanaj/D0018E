import db_connector

db = db_connector.db

def add_to_cart(cart_id, asset_id):
    if db.is_connected():
        cursor = db.cursor()
        cart_id = cart_id[0]
        check_query = "SELECT cart_items_assets_quantity FROM cart_items WHERE cart_items_cart_id = %s AND cart_items_assets_id = %s"
        cursor.execute(check_query, (cart_id, asset_id))
        result = cursor.fetchone()
        
        if result:
            new_quantity = result[0] + 1
            update_query = "UPDATE cart_items SET cart_items_assets_quantity = %s WHERE cart_items_cart_id = %s AND cart_items_assets_id = %s"
            cursor.execute(update_query, (new_quantity, cart_id, asset_id))
        else:
            insert_query = "INSERT INTO cart_items (cart_items_cart_id, cart_items_assets_id, cart_items_assets_quantity) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (cart_id, asset_id, 1))
        db.commit()
        cursor.close()
        print("Item added to cart")
        return True
    
def get_cart_items(cart_id):
    if db.is_connected():
        cursor = db.cursor(dictionary=True)
        query = '''
            SELECT assets_id, assets_type, assets_description, assets_price, assets_quantity, assets_img_name, cart_items_assets_quantity
            FROM cart_items
            JOIN new_assets ON cart_items.cart_items_assets_id = assets.assets_id
            WHERE cart_items_cart_id = %s
        '''
        cursor.execute(query, (cart_id,))
        cart_items = cursor.fetchall()
        cursor.close()
        return cart_items
    else:
        return None
    
def update_cart_item(cart_id, asset_id, quantity):
    if db.is_connected():
        cursor = db.cursor()
        query = "UPDATE cart_items SET cart_items_assets_quantity = %s WHERE cart_items_cart_id = %s AND cart_items_assets_id = %s"
        cursor.execute(query, (quantity, cart_id, asset_id))
        db.commit()
        cursor.close()
        return True
    else:
        return False
    
def remove_from_cart(cart_id, asset_id):
    if db.is_connected():
        cursor = db.cursor()
        query = "DELETE FROM cart_items WHERE cart_items_cart_id = %s AND cart_items_assets_id = %s"
        cart_id = cart_id[0] 
        cursor.execute(query, (cart_id, asset_id))
        db.commit()
        cursor.close()
        return True 
    else:
        return False

def clear_cart_items(cart_id):
    if db.is_connected():
        try:
            cursor = db.cursor()
            query = "DELETE FROM cart_items WHERE cart_items_cart_id = %s"
            cart_id = cart_id[0] 
            cursor.execute(query, (cart_id,))
            db.commit()
            cursor.close()
            print("Cart items cleared")
            return True 
        except:
            return False
    else:
        return False    

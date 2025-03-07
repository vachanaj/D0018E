import db_connector

db = db_connector.db

def add_to_cart(product_id, user_id):
    if db.is_connected():
        cursor = db.cursor()
        query = "INSERT INTO cart (cart_product_id, cart_user_id) VALUES (%s, %s)"
        cursor.execute(query, (product_id, user_id))
        db.commit()
        cursor.close()
        return True
    else:
        return False
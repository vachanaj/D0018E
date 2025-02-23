import sqlite3

def add_to_cart(user_id, asset_id):
    # Add product to cart


    asset_details = get_asset_details(asset_id)






#helper function for getting assets from asset table
def get_asset_details(asset_id):
    conn = sqlite3.connect('/home/irma/code/D0018E/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE id=?", (asset_id,))
    asset_details = cursor.fetchone()
    conn.close()
    return asset_details
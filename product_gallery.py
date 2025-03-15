import db_connector

db = db_connector.db


def get_all_assets():
    if db.is_connected():
        cursor = db.cursor()
        cursor.execute("SELECT * FROM assets")
        assets = cursor.fetchall()
        cursor.close()
        return assets
    else:
        return None
    
def get_asset(asset_id):
    if db.is_connected():
        cursor = db.cursor()
        query = "SELECT * FROM assets WHERE assets_id = %s"
        cursor.execute(query, (asset_id,))
        asset = cursor.fetchone()
        cursor.close()
        return asset
    else:
        return None

def get_asset_price(asset_id):
    if db.is_connected():
        cursor = db.cursor()
        query = "SELECT assets_price FROM assets WHERE assets_id = %s"
        cursor.execute(query, (asset_id,))
        price = cursor.fetchone()
        cursor.close()
        return price
    else:
        return None
    
def check_quantity(asset_id, quantity):
    print("asset_id and quantity", asset_id, quantity)
    if db.is_connected():
        cursor = db.cursor()
        query = "SELECT assets_quantity FROM assets WHERE assets_id = %s"
        cursor.execute(query, (asset_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] >= quantity
    else:
        return False
    

def decrease_quantity(asset_id, quantity):
    if db.is_connected():
        cursor = db.cursor()
        query = "UPDATE assets SET assets_quantity = GREATEST(assets_quantity - %s, 0) WHERE assets_id = %s"
        cursor.execute(query, (quantity, asset_id))
        db.commit()
        cursor.close()
        return True
    else:
        return False
    

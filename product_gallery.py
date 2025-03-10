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
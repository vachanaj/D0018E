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
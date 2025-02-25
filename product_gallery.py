import db_connector


def get_all_assets():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()
    conn.close()
    return assets
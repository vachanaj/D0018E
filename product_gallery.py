import db_connector


def get_all_assets():
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()
    conn.close()
    return assets
import db_connector

db = db_connector.db

def get_all_reviews():
    if db.is_connected():
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reviews")
        reviews = cursor.fetchall()
        cursor.close()
        return reviews
    else:
        return None
    
def add_review(user_id, asset_id, review_text):
    if db.is_connected():
        cursor = db.cursor()
        query = "INSERT INTO reviews (reviews_login_id, reviews_assets_id, reviews_text) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, asset_id, review_text))
        db.commit()
        cursor.close()
        return True
    else:
        return False
    
def delete_review(review_id):
    if db.is_connected():
        cursor = db.cursor()
        query = "DELETE FROM reviews WHERE reviews_id = %s"
        cursor.execute(query, (review_id,))
        db.commit()
        cursor.close()
        return True 
    else:
        return False

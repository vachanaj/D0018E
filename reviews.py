import db_connector

db = db_connector.db

    

#def get_all_reviews():
#    if db.is_connected():
#        cursor = db.cursor(dictionary=True)
#        cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")  # Fetch all reviews, sorted by creation time
#        reviews = cursor.fetchall()
#        cursor.close()
#        return reviews  # Return a flat list of reviews
#    return None


def get_all_reviews():
    if db.is_connected():
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM reviews 
            ORDER BY created_at DESC
        """)
        reviews = cursor.fetchall()
        cursor.close()

        # Organize reviews into a hierarchical structure
        review_dict = {}
        for review in reviews:
            if review['parent_review_id'] is None:
                # This is a top-level review
                review_dict[review['review_id']] = {  # Fixed: Added missing closing bracket
                    **review,
                    'replies': []
                }
            else:
                # This is a reply to a review
                if review['parent_review_id'] in review_dict:
                    review_dict[review['parent_review_id']]['replies'].append(review)

        # Convert the dictionary to a list of top-level reviews
        return list(review_dict.values())
    return None

def get_review_by_id(review_id):
    if db.is_connected():
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM reviews WHERE review_id = %s"
        cursor.execute(query, (review_id,))
        review = cursor.fetchone()  # Fetch a single review
        cursor.close()
        return review  # Return the review as a dictionary
    return None

def add_review(user_id, asset_id, review_text, rating=None, parent_review_id=None, author_role='customer'):
    if not db.is_connected():
        return False  # Database connection failed

    # Validate inputs
    if not user_id or not asset_id or not review_text:
        print("Error: user_id, asset_id, and review_text are required.")
        return False

    # Ensure rating is only set for customer reviews (not replies)
    if parent_review_id is not None:
        rating = None  # Replies (admin or customer) should not have a rating

    # Ensure rating is valid (1 to 5) if provided
    if rating is not None and (rating < 1 or rating > 5):
        print("Error: Rating must be between 1 and 5.")
        return False

    try:
        cursor = db.cursor()
        query = """
        INSERT INTO reviews 
        (review_login_id, review_asset_id, review_asset_rating, review_asset_comments, parent_review_id, author_role, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, asset_id, rating, review_text, parent_review_id, author_role))
        db.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error inserting review: {e}")
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

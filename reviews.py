import db_connector

db = db_connector.db

def add_review(user_id, asset_id, review_text, order_id, rating=None, parent_review_id=None, author_role='customer'):
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
    if rating is None:
        print("Error: Rating must be between 1 and 5.")
        return False

    try:
        cursor = db.cursor()
        query = """
        INSERT INTO reviews 
        (review_login_id, review_asset_id, review_asset_rating, review_asset_comments, parent_review_id, author_role, created_at, review_order_item_id) 
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
        """
        cursor.execute(query, (user_id, asset_id, rating, review_text, parent_review_id, author_role, order_id))
        db.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error inserting review: {e}")
        return False

def get_reviews_for_user_and_item(login_id, asset_id):
    if db.is_connected():
        print("Database connection successful")  # Debugging

        # Fetch all reviews for the given asset_id, ordered by review_id (or created_at) in ascending order
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT * FROM reviews 
            WHERE review_asset_id = %s
            ORDER BY review_id ASC  # Ensure parent reviews are processed first
        """
        cursor.execute(query, (asset_id,))
        reviews = cursor.fetchall()
        cursor.close()

        # Debugging: Print all fetched reviews
        print("Fetched reviews from database:", reviews)

        # Organize reviews into a hierarchical structure
        review_dict = {}
        for review in reviews:
            #print(f"Processing review: {review}")  # Debugging: Print each review being processed

            if review['parent_review_id'] is None:
                # This is a top-level review
                #print(f"Top-level review found: {review['review_id']}")  # Debugging
                review_dict[review['review_id']] = {
                    **review,
                    'replies': []
                }
            else:
                # This is a reply to a review
                #print(f"Reply found: {review['review_id']} (Parent ID: {review['parent_review_id']})")  # Debugging
                if review['parent_review_id'] in review_dict:
                    #print(f"Adding reply to parent review: {review['parent_review_id']}")  # Debugging
                    review_dict[review['parent_review_id']]['replies'].append(review)
                else:
                    print(f"Parent review not found for reply: {review['parent_review_id']}")  # Debugging

        # Debugging: Print the organized reviews
        #print("Organized reviews:", review_dict)

        # Filter reviews to only include those by the logged-in user
        user_reviews = [review for review in review_dict.values() if review['review_login_id'] == login_id]
        #print("Filtered user reviews:", user_reviews)  # Debugging: Print filtered reviews

        return user_reviews
    else:
        print("Database connection failed")  # Debugging
    return None

def get_login_id_by_username(username):
    if db.is_connected():
        cursor = db.cursor(dictionary=True)
        query = "SELECT login_id FROM login WHERE login_username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result['login_id']
        else:
            return None
    return None


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


#def add_review(user_id, asset_id, review_text, rating=None, parent_review_id=None, author_role='customer'):
#    if not db.is_connected():
#        return False  # Database connection failed

#    # Validate inputs
#    if not user_id or not asset_id or not review_text:
#        print("Error: user_id, asset_id, and review_text are required.")
#        return False
#
#    # Ensure rating is only set for customer reviews (not replies)
#    if parent_review_id is not None:
#        rating = None  # Replies (admin or customer) should not have a rating
#
#    # Ensure rating is valid (1 to 5) if provided
#    if rating is not None and (rating < 1 or rating > 5):
#        print("Error: Rating must be between 1 and 5.")
#        return False
#
#    try:
#        cursor = db.cursor()
#        query = """
#        INSERT INTO reviews 
#        (review_login_id, review_asset_id, review_asset_rating, review_asset_comments, parent_review_id, author_role, created_at) 
#        VALUES (%s, %s, %s, %s, %s, %s, NOW())
#        """
#        cursor.execute(query, (user_id, asset_id, rating, review_text, parent_review_id, author_role))
#        db.commit()
#        cursor.close()
#        return True
#    except Exception as e:
#        print(f"Error inserting review: {e}")
#        return False

#def add_review(user_id, asset_id, review_text, rating=None, parent_review_id=None, author_role='customer'):
#    if not db.is_connected():
#        return False  # Database connection failed
#
#    # Validate inputs
#    if not user_id or not asset_id or not review_text:
#        print("Error: user_id, asset_id, and review_text are required.")
#        return False
#
#    # Ensure rating is only set for customer reviews (not replies)
#    if parent_review_id is not None:
#        rating = None  # Replies (admin or customer) should not have a rating
#
#    # Ensure rating is valid (1 to 5) if provided
#    if rating is not None and (rating < 1 or rating > 5):
#        print("Error: Rating must be between 1 and 5.")
#        return False
#
#    try:
#        cursor = db.cursor()
#        query = """
#        INSERT INTO reviews 
#        (review_login_id, review_asset_id, review_asset_rating, review_asset_comments, parent_review_id, author_role, created_at) 
#        VALUES (%s, %s, %s, %s, %s, %s, NOW())
#        """
#        cursor.execute(query, (user_id, asset_id, rating, review_text, parent_review_id, author_role))
#        db.commit()
#        cursor.close()
#        return True
#    except Exception as e:
#        print(f"Error inserting review: {e}")
#        return False
    
def get_review_asset_rating(review_asset_id):
    if db.is_connected():
        cursor = db.cursor()
        query = """
            SELECT review_asset_id, SUM(review_asset_rating) as total_rating, COUNT(*) as rating_count
            FROM reviews
            WHERE review_asset_id = %s
            GROUP BY review_asset_id
        """
        cursor.execute(query, (review_asset_id,))
        result = cursor.fetchall()
        print(result)
        db.commit()
        cursor.close()

        total_rating = result[0][1]
        rating_count = result[0][2]
        average_rating = round(total_rating / rating_count)
            
        return average_rating
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

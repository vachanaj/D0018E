from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import stripe
import os
import user_transactions
import cart
import cart_items
import product_gallery
import orders
import order_items
import reviews
import datetime
from dotenv import load_dotenv
import db_connector 
import login  # Ensure correct import

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Load secret key from .env

# Set Stripe API keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

# Helper function to get database connection
def get_db_connection():
    conn = db_connector.get_connection()  # Assuming db_connector has a function to get a connection
    return conn

@app.route('/userhome')
def user_home():
    if 'username' in session:
        user_id = session.get('username')  # Get the logged-in user's ID
        asset_id = 1  # Hardcode the asset ID for now (replace with dynamic value later)

        # Fetch reviews for the logged-in user and the specific item
        reviews_data = reviews.get_reviews_for_user_and_item(user_id, asset_id)
        print("Fetched reviews:", reviews_data)  # Debugging: Print fetched reviews

        # Pass reviews to the template
        return render_template('userhome.html', reviews=reviews_data)
    else:
        # Redirect to the login page if the user is not logged in
        return redirect(url_for('login_user'))

@app.route('/customer/reply/<int:review_id>', methods=['POST'])
def customer_reply(review_id):
    data = request.get_json()
    print("Received data:", data)  # Debugging

    response_text = data.get('response')
    author_role = data.get('author_role', 'customer')  # Default to 'customer'
    user_id = session.get('username')  # Get the logged-in user's username

    if not response_text or not user_id:
        print("Invalid request: Missing response_text or user_id")  # Debugging
        return jsonify({'success': False, 'message': 'Invalid request'})

    # Fetch the original review to get the asset_id and login_id
    original_review = reviews.get_review_by_id(review_id)
    if not original_review:
        print("Original review not found")  # Debugging
        return jsonify({'success': False, 'message': 'Original review not found'})

    # Add the customer reply
    if reviews.add_review(
        user_id=user_id,
        asset_id=original_review['review_asset_id'],
        review_text=response_text,
        parent_review_id=review_id,  # Link to the latest admin reply
        author_role=author_role
    ):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to save response'})


@app.route('/admin/reply/<int:review_id>', methods=['POST'])
def admin_reply(review_id):
    data = request.get_json()
    print("Received data:", data)  # Debugging

    response_text = data.get('response')
    author_role = data.get('author_role', 'admin')  # Use 'admin' as the default role
    admin_id = 1  # Hardcode the admin ID or fetch it from a secure source

    print("Response text:", response_text)  # Debugging
    print("Author role:", author_role)  # Debugging

    if not response_text:
        print("Invalid request: Missing response_text")  # Debugging
        return jsonify({'success': False, 'message': 'Invalid request'})

    # Fetch the original review to get the asset_id
    original_review = reviews.get_review_by_id(review_id)
    if not original_review:
        print("Original review not found")  # Debugging
        return jsonify({'success': False, 'message': 'Original review not found'})

    # Add the admin reply
    if reviews.add_review(
        user_id=admin_id,
        asset_id=original_review['review_asset_id'],
        review_text=response_text,
        parent_review_id=review_id,  # Link to the original review
        author_role=author_role  # Use the author_role from the request
    ):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to save response'})


# Admin Dashboard Route
@app.route('/admin/dashboard')
def admin_page():
    if 'username' in session and session['role'] == 'admin':
        try:
            # Get the database connection from db_connector
            db = db_connector.db
            if db and db.is_connected():
                # Fetch assets
                cursor = db.cursor(dictionary=True)  # Use dictionary=True to get results as dictionaries
                cursor.execute('SELECT * FROM assets')  # Fetch all assets from the database
                assets = cursor.fetchall()  # Fetch all rows
                cursor.close()

                # Fetch reviews using the get_all_reviews function
                reviews_data = reviews.get_all_reviews()  # Fetch all reviews
                print("Fetched reviews:", reviews_data)  # Debugging: Print fetched reviews

                # Pass both assets and reviews to the template
                return render_template('admin.html', assets=assets, reviews=reviews_data)
            else:
                print("Database connection failed.")  # Debugging
                return "Database connection failed. Please check your connection.", 500
        except Exception as e:
            print(f"Error fetching data: {e}")  # Debugging
            return "An error occurred while fetching data.", 500
    return redirect(url_for('login'))  # Redirect to login if not an admin

@app.route('/admin/add-asset', methods=['POST'])
def add_asset():
    if 'username' in session and session['role'] == 'admin':
        try:
            # Get the data from the request (sent as JSON)
            data = request.json
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400

            # Extract fields from the data
            assets_type = data.get('assets_type')
            assets_desc = data.get('assets_desc')
            assets_price = data.get('assets_price')
            assets_quantity = data.get('assets_quantity')
            assets_img_name = data.get('assets_img_name')
            assets_rating = data.get('assets_rating') 

            # Ensure assets_rating is an integer (prevents errors)
            try:
                assets_rating = int(assets_rating)
            except ValueError:
                return jsonify({"success": False, "message": "Invalid assets_rating value"}), 400

            # Validate required fields
            if not all([assets_type, assets_price, assets_quantity, assets_rating]):
                return jsonify({"success": False, "message": "Missing required fields"}), 400

            # Get the database connection from db_connector
            db = db_connector.db
            if db and db.is_connected():
                cursor = db.cursor()
                # Insert the new asset into the database
                cursor.execute('''
                    INSERT INTO assets (assets_type, assets_desc, assets_price, assets_quantity, assets_img_name, assets_rating)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (assets_type, assets_desc, assets_price, assets_quantity, assets_img_name, assets_rating))
                db.commit()
                cursor.close()
                return jsonify({"success": True, "message": "Asset added successfully!"}), 201
            else:
                return jsonify({"success": False, "message": "Database connection failed"}), 500
        except Exception as e:
            print(f"Error adding asset: {e}")
            return jsonify({"success": False, "message": "An error occurred while adding the asset"}), 500
    return jsonify({"success": False, "message": "Unauthorized"}), 401


#delete asset route
@app.route('/admin/delete-asset/<int:assetId>', methods=['POST'])
def delete_asset(assetId):
    if 'username' in session and session['role'] == 'admin':
        try:
            # Get the database connection from db_connector
            db = db_connector.db
            if db and db.is_connected():
                cursor = db.cursor()

                # Delete the asset from the database
                cursor.execute('DELETE FROM assets WHERE assets_id = %s', (assetId,))
                db.commit()
                cursor.close()
                return jsonify({"success": True, "message": "Asset deleted successfully!"}), 200
            else:
                return jsonify({"success": False, "message": "Database connection failed"}), 500
        except Exception as e:
            print(f"Error deleting asset: {e}")
            return jsonify({"success": False, "message": "An error occurred while deleting the asset"}), 500
    return jsonify({"success": False, "message": "Unauthorized"}), 401

#Update asset route
@app.route('/admin/update-asset/<int:assetId>', methods=['POST'])
def update_asset(assetId):
    if 'username' in session and session['role'] == 'admin':
        try:
            # Get the data from the request (sent as JSON)
            data = request.json
            print("Received data for update:", data)  # Debugging: Print received data
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400

            # Extract fields from the data
            assets_type = data.get('assets_type')
            assets_desc = data.get('assets_desc')
            assets_price = data.get('assets_price')
            assets_quantity = data.get('assets_quantity')
            assets_img_name = data.get('assets_img_name')

            # Validate required fields
            if not all([assets_type, assets_price, assets_quantity]):
                return jsonify({"success": False, "message": "Missing required fields"}), 400

            # Get the database connection from db_connector
            db = db_connector.db
            if db and db.is_connected():
                cursor = db.cursor()

                # Update the asset in the database
                cursor.execute('''
                    UPDATE assets 
                    SET assets_type = %s, assets_desc = %s, assets_price = %s, assets_quantity = %s, assets_img_name = %s
                    WHERE assets_id = %s
                ''', (assets_type, assets_desc, assets_price, assets_quantity, assets_img_name, assetId))
                db.commit()
                cursor.close()
                return jsonify({"success": True, "message": "Asset updated successfully!"}), 200
            else:
                return jsonify({"success": False, "message": "Database connection failed"}), 500
        except Exception as e:
            print(f"Error updating asset: {e}")  # Debugging: Print the error
            return jsonify({"success": False, "message": "An error occurred while updating the asset"}), 500
    return jsonify({"success": False, "message": "Unauthorized"}), 401

@app.route('/admin/add-admin')
def add_admin():
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin.html', section='add-admin')  # Admin dashboard page
    else:
        return redirect(url_for('login'))  # Redirect to login if not an admin


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate login credentials (using your login validation function)
        user = login.validate_login(username, password)  # Assuming this function fetches user details from DB
        
        if user:
            # Store user information in session
            session['userfirst'] = user['login_first_name']
            session['userlast'] = user['login_last_name']
            session['username'] = user['login_username']
            session['role'] = user['login_role']
            session['useremail'] = user['login_email']

            # Check if the user is an admin or normal user
            if user['login_role'] == 'admin':
                #return redirect(url_for('admin_page'))  # Redirect to admin page if admin
                return redirect(url_for('index', username=user['login_username']))  # Redirect normal users to homepage with session info
            else:
                login_id = login.get_login_id(session['username'])
                cart.create_cart(login_id)  # Get user's cart
                return redirect(url_for('index', username=user['login_username']))  # Redirect normal users to homepage with session info
            
        else:
            return redirect('/error-page')  # Invalid credentials, redirect to error page

    return render_template('login.html')  # Show login form if GET request

@app.route('/logout')
def logout():
    cart_id = cart.get_cart_id(login.get_login_id(session['username']))
    print("cart_id", cart_id)
    cart_items.clear_cart_items(cart_id)  # Clear user's cart on logout
    cart.delete_cart(cart_id)  # Delete user's cart on logout
    
    print("before logout!", session['username'])
    session.pop('username', None)
    session.pop('role', None)

    
    print("Logged out successfully!")
    return redirect('/')  # back to start after logout

@app.route('/user-info')
def user_info():
    if 'username' in session:
        print("user info for user:", session['username'])
        
        # Check if the user is an admin or normal user
        if session['role'] == 'admin':
            return redirect(url_for('admin_page'))  # Redirect to admin page if admin
        else:
            login_id = login.get_login_id(session['username'])
            print("login Id: ", login_id)
            cust_order_ids = orders.get_order_ids(login_id)
            print("order Ids: ", cust_order_ids)
            cust_orders = []
            for orderid in cust_order_ids:
                singleOrderitems = order_items.get_order_items(orderid[0])
                print("single order items", singleOrderitems)
                cust_orders.append({
                    'order_id': orderid[0],
                    'order_total_price': orderid[2],
                    'order_status': orderid[3],
                    'order_timestamp': orderid[4],
                    'single_order_items': singleOrderitems
                })
            #print("cust_orders: ", cust_orders)
            username = session['username']  # Get the logged-in user's username
            asset_id = 2  # Hardcode the asset ID for now (replace with dynamic value later)

            # Fetch the login_id for the logged-in user
            review_login_id = reviews.get_login_id_by_username(username)  # Use reviews.get_login_id_by_username
            #if not login_id:
                #return jsonify({'success': False, 'message': 'User not found'})

            print(f"Fetching reviews for login_id: {review_login_id}, asset_id: {asset_id}")  # Debugging

            # Fetch reviews for the logged-in user and the specific item
            reviews_data = reviews.get_reviews_for_user_and_item(review_login_id, asset_id)
            print("Fetched reviews:", reviews_data)  # Debugging: Print fetched reviews

            # Pass reviews to the template
            return render_template('userhome.html', cust_orders=cust_orders, reviews=reviews_data)
    else:
        # Redirect to the login page if the user is not logged in
        return redirect(url_for('login_user'))       


@app.route('/')
def index():
    assets = product_gallery.get_all_assets()
    print("assets:", assets)
    reviews_by_asset = reviews.get_all_reviews()  # Now it's grouped by asset_id
    print("reviews_by_asset:", reviews_by_asset)
    if 'username' in session:
        print("session:", session['username'])
        login_id = login.get_login_id(session['username'])
        cart_id = cart.get_cart_id(login_id)
        print(cart_id)
        if cart_id is None:
            return render_template('index.html', assets=assets, reviews_by_asset=reviews_by_asset)
        else:
            cartItems = cart_items.get_cart_items(cart_id)
            print("cart items in default route: ", cartItems)
            return render_template('index.html', assets=assets, reviews_by_asset=reviews_by_asset, cart_items=cartItems)
        
    return render_template('index.html', assets=assets, reviews_by_asset=reviews_by_asset)


@app.route('/db-test')
def db_test():
  if db_connector.dbtester():
    return "Database test successful!"
  else:
    return "Database test failed!"

@app.route('/error-page')
def error_page():
  return "Login failed!"

@app.route('/register')
def registration_page():
  return render_template('registration.html')

@app.route('/newuser', methods=['POST'])
def register_user():
  if request.method == 'POST':
    print("register POST request")
    first = request.form['first']
    last = request.form['last']
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    # Process the login data
    result = login.register_user(first, last, username, password, email)
    if result:
      return redirect('/')
    else:
      return redirect('/error-page')

@app.route('/newadmin', methods=['POST'])
def register_admin_route():
  if request.method == 'POST':
    print("register POST request")
    first = request.form['first']
    last = request.form['last']
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    # Process the login data
    result = login.register_admin(first, last, username, password, email)  # Call the imported function directly
    if result:
      return jsonify({"success": True, "message": "Admin registered successfully"})
    else:
      return jsonify({"success": False, "message": "Failed to register admin"})

@app.route('/update_cart', methods=['GET', 'POST'])
def update_cart():
    data = request.json  # Get product data from frontend
    print("request data: ", data)
    iord = data['operation']
    productId = data['productId']
    login_id =  login.get_login_id(session['username'])
    cart_id = cart.get_cart_id(login_id)
    cart_items.update_cart_item_op(cart_id, productId, iord) # incr/decr product from cart
    return jsonify({"message": f"{productId} cart updated"})  # Send response

@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    productId = request.json  # Get product data from frontend
    print("Added to Cart:", productId)  # Print to console (or process further)

    #product_gallery.decrease_quantity(data['productId'], 1)  # Decrease product quantity
    #login_id = login.get_login_id(data['loginUsername'])  # Get login ID from session
    
    login_id =  login.get_login_id(session['username'])
    cart_id = cart.get_cart_id(login_id)
    cart_items.add_to_cart(cart_id, productId)  # Add product to cart
    # You can store this in a database or session
    return jsonify({"message": f"{productId} added to cart!"})  # Send response

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    productId = request.json  # Get product data from frontend
    print("Removed from Cart:", productId)  # Print to console (or process further)
    
    #product_gallery.increase_quantity(data['productId'], 1)  # Increase product quantity
    login_id =  login.get_login_id(session['username']) # Get login ID from session
    cart_id = cart.get_cart_id(login_id)
    cart_items.remove_from_cart(cart_id, productId)  # Remove product from cart
    # You can store this in a database or session
    return jsonify({"message": f"{productId} removed from cart!"})  # Send response

@app.route('/get_cart_items')
def get_cart_items():
    login_id = login.get_login_id(session['username'])  # Get login ID from session
    cart_id = cart.get_cart_id(login_id)         # Get cart ID from login ID    
    #cartItem = cart_items.get_recent_cart_item(cart_id)
    cartItems = cart_items.get_cart_items(cart_id)  # Get all cart items from cart ID
    print("cartItems:", cartItems)  # Debugging: Print cart items
    return jsonify(cartItems)  # Send cart items as JSON response

@app.route('/shoppingcart')
def shoppingcart():
    return render_template('shoppingcart.html', public_key=PUBLIC_KEY)

# @app.route('/create-checkout-session', methods=['POST'])
# def create_checkout_session():
#     try:
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                 {
#                     'price_data': {
#                         'currency': 'usd',
#                         'product_data': {
#                             'name': 'Sample Item'
#                         },
#                         'unit_amount': 2000,  # $20.00 in cents
#                     },
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             success_url=request.host_url + 'checkout-success',
#             cancel_url=request.host_url + 'shoppingcart',
#         )
#         return jsonify({'url': session.url})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    
    #yes it does need to be this stupid for some reason, could make it nicer with more time maybe, now it works
    try:
        username = session['username']
        if not username:
            return jsonify({'error': 'User not logged in'}), 401

        login_id = login.get_login_id(username)
        cart_id_tuple = cart.get_cart_id(login_id)
        print("cart_id_tuple", cart_id_tuple)
        cart_id = cart_id_tuple[0] if isinstance(cart_id_tuple, tuple) else cart_id_tuple

        if not cart_id or not isinstance(cart_id, int):
            return jsonify({'error': 'Invalid cart ID'}), 400

        conn = db_connector.db  # Use the MySQL connection from db_connector
        cursor = conn.cursor()

        # Fetch cart items for the current user
        cursor.execute("""
            SELECT a.assets_id, a.assets_desc, a.assets_price, c.cart_items_assets_quantity
            FROM cart_items c
            JOIN assets a ON c.cart_items_assets_id = a.assets_id
            WHERE c.cart_items_cart_id = %s
        """, (cart_id,))  # ✅ Ensure cart_id is a single integer, not a tuple

        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({'error': 'No items in cart'}), 400

        total_price = 0  # Initialize total_price
            
        line_items = []
        for item in cart_items:
            
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item[1],  # assets_desc
                    },
                    'unit_amount': int(item[2] * 100),  # assets_price in cents
                },
                'quantity': item[3],  # cart_items_assets_quantity
            })

        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.host_url + 'checkout-success',
            cancel_url=request.host_url,
        )

        print("stripe_session created")
        
        
        
        cursor.close()

        return jsonify({'url': stripe_session.url})
    except Exception as e:
        print(f"Error creating checkout session: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500



@app.route('/checkout-success')
def checkout_success():
    if 'username' in session:
        total_price = 0
        try:
            print("checkout success for:", session['username'])
            login_id = login.get_login_id(session['username'])
            cart_id = cart.get_cart_id(login_id)
            cartItems = cart_items.get_cart_items(cart_id)

            for item in cartItems:
                print("item", item)
                assetId = item['assets_id']
                print("assetId", assetId)
                itemQuantity = item['cart_items_assets_quantity']
                
                print(itemQuantity)
                inStock = product_gallery.check_quantity(assetId, itemQuantity)
                if not inStock:
                    print("item in stock")
                    return jsonify({'error': 'Item out of stock'}), 400
                else:
                    print("Decreasing quantity for assetId:", assetId)
                    product_gallery.decrease_quantity(assetId, itemQuantity)

            for item in cartItems:
                assetId = item['assets_id']
                print("assetId: ",assetId)
                itemQuantity = item['cart_items_assets_quantity']

                assetPrice = product_gallery.get_asset_price(assetId)
                total_asset_price = assetPrice[0] * itemQuantity
                total_price += total_asset_price
                print("Total price:", total_price)

            # Add order to the database
            orders.create_order(login_id, total_price, datetime.datetime.now())
            print("Order created successfully!")
            order_id = orders.get_order_id(login_id)

            for item in cartItems:
                assetId = item['assets_id']
                itemQuantity = item['cart_items_assets_quantity']
                assetPrice = product_gallery.get_asset_price(assetId)
                print("Adding order item for assetId:", assetId)
                print("Order ID:", order_id)
                print("Item Quantity:", itemQuantity)
                print("Asset Price:", assetPrice)
                order_items.add_order_item(order_id, assetId, itemQuantity, assetPrice)
                print("Order item added successfully!")


            # Clear the cart items and delete the cart
            cart_items.clear_cart_items(cart_id)
            cart.delete_cart(cart_id)
            print(f"Cart cleared for user: {session['username']}")
    
        except Exception as e:
            print(f"Error clearing cart after checkout: {e}")

    return render_template("checkoutsuccess.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



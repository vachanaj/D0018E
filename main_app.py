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


# Admin Dashboard Route
@app.route('/admin/dashboard')
def admin_page():
    if 'username' in session and session['role'] == 'admin':
        try:
            # Get the database connection from db_connector
            db = db_connector.db
            if db and db.is_connected():
                cursor = db.cursor(dictionary=True)  # Use dictionary=True to get results as dictionaries
                cursor.execute('SELECT * FROM assets')  # Fetch all assets from the database
                assets = cursor.fetchall()  # Fetch all rows
                cursor.close()
                return render_template('admin.html', assets=assets)  # Pass assets to the template
            else:
                return "Database connection failed. Please check your connection.", 500
        except Exception as e:
            print(f"Error fetching assets: {e}")
            return "An error occurred while fetching assets.", 500
    return redirect(url_for('login'))  # Redirect to login if not an admin

# Add Asset Route
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
            assets_description = data.get('assets_description')
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
                # Insert the new asset into the database
                cursor.execute('''
                    INSERT INTO assets (assets_type, assets_description, assets_price, assets_quantity, assets_img_name, assets_rating)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (assets_type, assets_description, assets_price, assets_quantity, assets_img_name, 1))
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
            assets_description = data.get('assets_description')
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
                    SET assets_type = %s, assets_description = %s, assets_price = %s, assets_quantity = %s, assets_img_name = %s
                    WHERE assets_id = %s
                ''', (assets_type, assets_description, assets_price, assets_quantity, assets_img_name, assetId))
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
            session['username'] = user['login_username']
            session['role'] = user['login_role']

            # Check if the user is an admin or normal user
            if user['login_role'] == 'admin':
                return redirect(url_for('admin_page'))  # Redirect to admin page if admin
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

@app.route('/')
def index():
    assets = product_gallery.get_all_assets()
    print(assets)

    #reviews = reviews.get_all_reviews()
    return render_template('index.html', assets=assets)


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
      return redirect('/welcome-page')
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

@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    data = request.json  # Get product data from frontend
    print("Added to Cart:", data)  # Print to console (or process further)

    #product_gallery.decrease_quantity(data['productId'], 1)  # Decrease product quantity
    login_id = login.get_login_id(data['loginUsername'])  # Get login ID from session
    cart_id = cart.get_cart_id(login_id)
    cart_items.add_to_cart(cart_id, data['productId'])  # Add product to cart
    # You can store this in a database or session
    return jsonify({"message": f"{data['productName']} added to cart!"})  # Send response

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json  # Get product data from frontend
    print("Removed from Cart:", data)  # Print to console (or process further)
    
    #product_gallery.increase_quantity(data['productId'], 1)  # Increase product quantity
    login_id = login.get_login_id(data['loginUsername'])  # Get login ID from session
    cart_id = cart.get_cart_id(login_id)
    cart_items.remove_from_cart(cart_id, data['productId'])  # Remove product from cart
    # You can store this in a database or session
    return jsonify({"message": f"{data['name']} removed from cart!"})  # Send response

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
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not logged in'}), 401

        login_id = login.get_login_id(username)
        cart_id_tuple = cart.get_cart_id(login_id)
        cart_id = cart_id_tuple[0] if isinstance(cart_id_tuple, tuple) else cart_id_tuple

        #cartItems = cart_items.get_cart_items(cart_id)
               
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
            assetId = item[0]
            itemQuantity = item[3]
            inStock = product_gallery.check_quantity(assetId, itemQuantity)
            if not inStock:
                return jsonify({'error': 'Item out of stock'}), 400
            else:
                print("Decreasing quantity for assetId:", assetId)
                product_gallery.decrease_quantity(assetId, itemQuantity)

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
            cancel_url=request.host_url + 'shoppingcart',
        )

        print("stripe_session created")
        
        for item in cart_items:
            assetId = item[0]
            itemQuantity = item[3]

            assetPrice = product_gallery.get_asset_price(assetId)
            total_asset_price = assetPrice[0] * itemQuantity
            total_price += total_asset_price
            print("Total price:", total_price)

        # Add order to the database
        # orders.create_order(login_id, total_price, datetime.datetime.now())
        # print("Order created successfully!")
        # order_id = orders.get_order_id(login_id)

        # for item in cart_items:
        #     assetId = item[0]
        #     itemQuantity = item[3]
        #     assetPrice = product_gallery.get_asset_price(assetId)
        #     order_items.add_order_item(order_id, assetId, itemQuantity, assetPrice)
        #     print("Order item added successfully!")

        
        
        cursor.close()

        return jsonify({'url': stripe_session.url})
    except Exception as e:
        print(f"Error creating checkout session: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500



@app.route('/checkout-success')
def checkout_success():
    if 'username' in session:
        try:
            cart_id = cart.get_cart_id(login.get_login_id(session['username']))
            # Clear the cart items and delete the cart
            cart_items.clear_cart_items(cart_id)
            cart.delete_cart(cart_id)
            print(f"Cart cleared for user: {session['username']}")
        
        except Exception as e:
            print(f"Error clearing cart after checkout: {e}")

    return "Checkout Successful! Thank you for your purchase."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



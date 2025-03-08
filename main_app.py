from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import stripe
import os
import user_transactions
import cart
from dotenv import load_dotenv
import db_connector 
from login import validate_login, register_admin  # Ensure correct import

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
                    INSERT INTO assets (assets_type, assets_description, assets_price, assets_quantity, assets_img_name)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (assets_type, assets_description, assets_price, assets_quantity, assets_img_name))
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
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate login credentials (using your login validation function)
        user = validate_login(username, password)  # Assuming this function fetches user details from DB
        
        if user:
            # Store user information in session
            session['username'] = user['login_username']
            session['role'] = user['login_role']

            # Check if the user is an admin or normal user
            if user['login_role'] == 'admin':
                return redirect(url_for('admin_page'))  # Redirect to admin page if admin
            else:
                return redirect(url_for('index'))  # Redirect normal users to homepage
            
        else:
            return redirect('/error-page')  # Invalid credentials, redirect to error page

    return render_template('login.html')  # Show login form if GET request

@app.route('/')
def index():
    return render_template('index.html')

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
    # Process the login data
    result = login.register_user(first, last, username, password)
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
    # Process the login data
    result = register_admin(first, last, username, password)  # Call the imported function directly
    if result:
      return jsonify({"success": True, "message": "Admin registered successfully"})
    else:
      return jsonify({"success": False, "message": "Failed to register admin"})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json  # Get product data from frontend
    print("Added to Cart:", data)  # Print to console (or process further)

    cart.add_to_cart(data)
    # You can store this in a database or session
    return jsonify({"message": f"{data['name']} added to cart!"})  # Send response

@app.route('/shoppingcart')
def shoppingcart():
    return render_template('shoppingcart.html', public_key=PUBLIC_KEY)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Sample Item'
                        },
                        'unit_amount': 2000,  # $20.00 in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'checkout-success',
            cancel_url=request.host_url + 'shoppingcart',
        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/checkout-success')
def checkout_success():
    return "Checkout Successful! Thank you for your purchase."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



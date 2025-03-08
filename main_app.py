from flask import Flask, render_template, request, redirect, jsonify
import stripe
import os
import user_transactions
import login
import cart
import product_gallery
from dotenv import load_dotenv
import db_connector

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set Stripe API keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

@app.route('/')
def index():
    assets = product_gallery.get_all_assets()
    return render_template('index.html', assets=assets)

@app.route('/db-test')
def db_test():
  if db_connector.dbtester():
    return "Database test successful!"
  else:
    return "Database test failed!"

@app.route('/login', methods=['GET','POST'])
def login_data():
  if request.method == 'POST':
    print("login POST request")
    username = request.form['username']
    
    password = request.form['password']
    # Process the login data
    result = login.validate_login(username, password)
    if result:
       data = {"isLoggedIn": True}
       return jsonify(data)
    else:
       return redirect('/error-page')
  if request.method == 'GET':
    return render_template('login.html')

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

from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import stripe
import os
import user_transactions
from dotenv import load_dotenv
from db_connector import validate_login

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Load secret key from .env

# Set Stripe API keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = validate_login(username, password)  # Fetch user details

        if user:
            session['username'] = user['login_username']
            session['role'] = user['login_role']

            if user['login_role'] == 'admin':
                return redirect(url_for('admin_page'))
            else:
                return redirect(url_for('index'))  # Redirect normal users to homepage

        return "Invalid credentials, try again!"

    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin.html')
    else:
        return redirect(url_for('login'))



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

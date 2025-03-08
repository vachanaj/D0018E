import db_connector
import stripe
import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def update_tables():
    conn = sqlite3.connect('/home/irma/code/D0018E/database.db')
    cursor = conn.cursor()

    # Example: Insert into transactions table
    #cursor.execute("INSERT INTO transactions (user_id, item, quantity, price) VALUES (?, ?, ?, ?)", 
    #               (1, "T-shirt", 2, 2000))

    cursor.execute("SELECT * FROM item_cart")

    conn.commit()
    conn.close()

    return True

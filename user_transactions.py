import db_connector
import stripe
import os
import sqlite3
from dotenv import load_dotenv


#def update_tables(cust_cart):
    # Update the tables
    #cursor = db.cursor() 
    #cursor.execute("DELETE FROM cart")
   #cursor.execute("INSERT INTO transactions")

    #db.commit()
    #db.close()

#   return True


# Helper function for getting assets from asset table
# def get_asset_details(asset_id):
#     conn = sqlite3.connect('/home/irma/code/D0018E/database.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM assets WHERE id=?", (asset_id,))
#     asset_details = cursor.fetchone()
#     conn.close()
#     return asset_details 


# Load environment variables
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def update_tables():
    conn = sqlite3.connect('/home/irma/code/D0018E/database.db')
    cursor = conn.cursor()

    # Example: Insert into transactions table
    cursor.execute("INSERT INTO transactions (user_id, item, quantity, price) VALUES (?, ?, ?, ?)", 
                   (1, "T-shirt", 2, 2000))

    conn.commit()
    conn.close()

    return True

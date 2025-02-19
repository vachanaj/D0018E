from flask import Flask, render_template, request, redirect
import db_connector

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')    


@app.route('/db-test')
def db_test():
  if db_connector.dbtester():
    return "Database test successful!"
  else:
    return "Database test failed!"


"""@app.route('/login', methods=['POST'])
def login_data():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    # Process the login data
    result = db_connector.validate_login(username, password)
    if result:
      return redirect('/welcome-page')
    else:
      return "Login failed!"
    return redirect('/login-page')"""


@app.route('/login')
def login_data():
    username = "Irma1"
    password = "admin"
    # Process the login data
    result = db_connector.validate_login(username, password)
    if result:
      return "found"
    else:
      return "Login failed!"


"""@app.route('/welcome-page')

@app.route('/login-page')"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

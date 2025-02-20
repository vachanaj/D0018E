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


@app.route('/login', methods=['GET','POST'])
def login_data():
  if request.method == 'POST':
    print("login POST request")
    username = request.form['username']
    
    password = request.form['password']
    # Process the login data
    result = db_connector.validate_login(username, password)
    if result:
      return redirect('/welcome-page')
    else:
      return redirect('/error-page')

  if request.method == 'GET':
    return render_template('login.html')
    
@app.route('/welcome-page')
def welcome_page():
  
  return render_template('userhome.html')

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
    result = db_connector.register_user(first, last, username, password)
    if result:
      return redirect('/welcome-page')
    else:
      return redirect('/error-page')


"""@app.route('/login')
def login_data():
    username = "Irma1"
    password = "admin"
    # Process the login data
    result = db_connector.validate_login(username, password)
    if result:
      return "found"
    else:
      return "Login failed!"




@app.route('/login-page')"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

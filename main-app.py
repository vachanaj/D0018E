from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates/registration.html')
def registration():
    return render_template('registration.html')

@app.route('/templates/userhome.html')
def userhome():
    return render_template('/templates/userhome.html')

@app.route('/templates/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Only process form if method is POST
        username = request.form['form2Example1']
        password = request.form['form2Example2']

        # Example validation (replace with actual DB check)
        if username == "admin" and password == "password123.":
            return "Login successful!"
        else:
            return "Login failed!"

    # If it's a GET request, just show the login form
    return render_template('login.html')  # Ensures template is rendered first

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, render_template
app = Flask(__name__) 

@app.route('/')
def index():

    return render_template('index.html') 


@app.route('/sign-in')
def sign_in():
    return render_template('sign-in.html')

@app.route('/authenticate')
def authenticate():
    # call User.auth_master_user
    return redirect(url_for('index'))

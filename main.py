import os
import datetime

from flask import Flask, render_template, request, redirect, url_for, session

from models.model import User

app = Flask(__name__) 
app.secret_key = os.getenv('FLASK_SECRET_KEY')

@app.route('/')
def index():
    if 'session_token' in session:
        session_token = session['session_token']
        if User.auth_master_user_session_token(session_token):
            return render_template('index.html') 

    return redirect(url_for('sign_in_master'))

@app.route('/sign-in-master')
def sign_in_master():
    return render_template('sign-in.html')

@app.route('/authenticate-master', methods=['POST'])
def authenticate_master():
    password = request.form['password']
    session_token = User.auth_master_user(password)
    if session_token:
        session['session_token'] = session_token 
        return redirect(url_for('index'))

    return 'Wong password!'


# route for edit transaction
# route for new transaction

#route for new category item

def show_monthly_grocery(month=None, year=None):
    today = datetime.datetime.today()
    month = month or today.month 
    year = year or today.year

    transactions = Transaction.get_by_month(month, year)

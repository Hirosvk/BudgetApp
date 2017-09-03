import os
import datetime

from flask import Flask, render_template, request, redirect, url_for, session

from models.model import User, Transaction, Limit, Category, BudgetType, Limit
import utils

app = Flask(__name__) 
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# TODO:
#   Edit/Insert new limit
#   Previous month transactions


@app.route('/')
def index():
    if 'session_token' in session:
        session_token = session['session_token']
        if User.auth_master_user_session_token(session_token):
            return show_monthly_grocery() 

    return redirect(url_for('sign_in_master'))

@app.route('/grocery/<int:month>/<int:year>')
def grocery(month, year):
    next_page = '/grocery/{}/{}'.format(month, year)
    return show_monthly_grocery(is_current_month=False, month=month, year=year, next_page=next_page)

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

    return 'Wrong password!'


@app.route('/edit-transaction/<int:_id>')
def edit_transaction(_id):
    next_page = request.args.get('next_page')
    row_data = Transaction.get_row_by_id(_id, as_dict=True)

    categories = Category.get_all_names()
    budget_types = BudgetType.get_all_names()

    temp_vars = {
        '_id': _id,
        'row_data': row_data,
        'categories': categories,
        'budget_types': budget_types,
        'next_page': next_page
    }

    if row_data:
        return render_template('edit_transaction.html', **temp_vars)

@app.route('/update-transaction/<int:_id>', methods=['POST'])
def update_transaction(_id):
    amount = int(request.form['amount'])
    next_page = request.form['next_page']

    budget_type = request.form['budget_type']
    category = request.form['category']
    marchant = request.form['marchant']
    date = request.form['date']
    description = request.form['description']

    if not _id:
        Transaction.insert(date, description, amount, budget_type, category, marchant)
        
    else:
        Transaction.update_by_id(_id, date, description, amount, budget_type, category, marchant)

    return redirect(next_page) 

@app.route('/delete-transaction/<int:_id>', methods=['POST'])
def delete_transaction(_id):
    Transaction.delete_by_id(_id)
    next_page = request.form['next_page']
    return redirect(next_page)

@app.route('/adjust-from-last-month-balance/<int:this_month>/<int:this_year>', methods=['POST'])
def adjust_from_last_month_balance(this_month, this_year):
    if this_month == 1:
        last_month = 12
        this_year -= 1    
    else:
        last_month = this_month - 1
        
    last_month_limit = Limit.get_amount_by_month(last_month, this_year)
    last_month_total_spending = Transaction.get_total_spending(last_month, this_year)

    if last_month_limit: 
        date = datetime.datetime(year=this_year, month=this_month, day=1)
        description = 'Adjusted balance from {}/{}'.format(last_month, this_year)
        amount = last_month_limit - last_month_total_spending
        amount = amount * -1

        Transaction.insert(date, description, amount)
    
    next_page = request.form['next_page']
    return redirect(next_page)


@app.route('/change-monthly-limit/<int:month>/<int:year>', methods=['POST'])
def change_monthly_limit(month, year):
    new_amount = int(request.form['new_amount'])
    Limit.change_limit(month, year, new_amount)

    next_page = request.form['next_page']
    return redirect(next_page)


def show_monthly_grocery(is_current_month=True, month=None, year=None, next_page='/'):
    today = datetime.datetime.today() - datetime.timedelta(hours=8)
    month = month or today.month 
    year = year or today.year
    day = today.day

    transactions = Transaction.get_by_month(month, year)
    spent_so_far = Transaction.get_total_spending(month, year)
    this_month_limit = Limit.get_amount_by_month(month, year) or 0
    remaining_amt = this_month_limit - spent_so_far

    spending_track = '' 
    if this_month_limit:
        spending_track = utils.get_spending_track(spent_so_far, this_month_limit, month)

    template_var = {
        'transactions': transactions,
        'this_month_limit': this_month_limit,
        'spent_so_far': spent_so_far,
        'remaining_amt': remaining_amt,
        'day': str(day),
        'month': str(month),
        'year': str(year),
        'spending_track': str(spending_track),
        'next_page': next_page,
        'is_current_month': is_current_month
    }

    return render_template('list_transactions.html', **template_var)

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = os.getenv('APP_PORT') 
    app.run(host=host, port=port)

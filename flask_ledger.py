from flask import (Flask, g, render_template,
                   flash, redirect, url_for,
                   abort)

from forms import CreateAccountForm
from models import (Account, DATABASE, Entry, initialize,
                    Transfer, )

from peewee import OperationalError

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = "aasdfasdf;aosihasgo*(&^Uhkewjd7efI&%$iygkjbsd"


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = DATABASE
    try:
        g.db.connect()
    except OperationalError:
        pass


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/create_account', methods=('GET', 'POST'))
def create_account():
    form = CreateAccountForm()
    if form.validate_on_submit():
        Account.create_account(
            name=form.name.data.strip(),
            balance=form.balance.data,
            accnt_type=form.accnt_type.data,
            bank=form.bank.data.strip(),
        )
        flash('Account Successfully Created', category='success')
        return redirect(url_for('index'))
    return render_template('create_account.html', form=form)


@app.route('/')
def index():
    accounts = Account.select()
    return render_template('index.html', accounts=accounts)


if __name__ == "__main__":
    initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)

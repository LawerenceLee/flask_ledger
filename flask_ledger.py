from flask import (Flask, g, render_template,
                   flash, redirect, url_for,
                   abort)

from forms import CreateAccountForm, CreateEntryForm, CreateTransferForm
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
        try:
            Account.create_account(
                name=form.name.data.strip(),
                balance=form.balance.data,
                accnt_type=form.accnt_type.data,
                bank=form.bank.data.strip(),
            )
        except Exception as e:
            flash('An error occured in creating your account',
                  category='failure')
            flash(e, category='failure')
        else:
            flash('Account Successfully Created', category='success')
            return redirect(url_for('index'))
    return render_template('create_account.html', form=form)


@app.route('/create_entry', methods=('GET', 'POST'))
def create_entry():
    form = CreateEntryForm()
    form.assc_accnt.choices = [(str(account.id), account.name)
                               for account in Account.select()]

    if form.assc_accnt.choices == []:
        flash('Need to create an Account first', category='failure')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        assc_accnt = Account.select().where(
            Account.id == form.assc_accnt.data).get()
        try:
            Entry.create_entry(
                descrip=form.descrip.data,
                date=form.date.data,
                tranact_type=form.tranact_type.data,
                amount=form.amount.data,
                assc_accnt=assc_accnt,
            )
        except Exception as e:
            flash('An error occured in creating your entry',
                  category='failure')
            flash(e, category='failure')
        else:
            lst_entry = Entry.select().count()
            entry = Entry.select().where(Entry.id == lst_entry).get()
            entry.mk_accnt_chgs()
            flash('Entry Created', category='success')
            return redirect(url_for('index'))
    return render_template('create_entry.html', form=form)


@app.route('/create_transfer', methods=('GET', 'POST'))
def create_transfer():
    form = CreateTransferForm()
    choices = [(str(account.id), account.name)
               for account in Account.select()]
    form.from_accnt.choices = choices
    form.to_accnt.choices = choices

    if len(form.from_accnt.choices) < 2:
        flash('Need to create two Accounts first', category='failure')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        from_accnt = Account.select().where(
            Account.id == form.from_accnt.data).get()
        to_accnt = Account.select().where(
            Account.id == form.to_accnt.data).get()

        if form.from_accnt.data == form.from_accnt.data:
            flash(
                'May not use the same account for To and From Account Fields',
                category='failure'
            )
            render_template('create_transfer.html', form=form)

        try:
            Transfer.create_transfer(
                descrip=form.descrip.data,
                date=form.date.data,
                amount=form.amount.data,
                from_accnt=from_accnt,
                to_accnt=to_accnt,
            )
        except Exception as e:
            flash(e, category='failure')
        else:
            lst_transfer = Transfer.select().count()
            transfer = Transfer.select().where(
                Transfer.id == lst_transfer).get()
            transfer.mk_transfer()
            flash('Transfer Successful', category='success')
            return redirect(url_for('index'))
    return render_template('create_transfer.html', form=form)


@app.route('/')
def index():
    accounts = Account.select()
    return render_template('index.html', accounts=accounts)


if __name__ == "__main__":
    initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)

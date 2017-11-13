from flask_wtf import FlaskForm
from wtforms import (DateField, DecimalField,
                     StringField, SelectField,
                     )
from wtforms.validators import (DataRequired, ValidationError)

from not_equal_validator import NotEqualTo
from models import Account

from models import Account, Entry, Transfer


def account_exists(form, field):
    if Account.select().where(Account.name == field.data).exists():
        raise ValidationError('Account with that name already exists.')


class CreateAccountForm(FlaskForm):
    name = StringField(
        'Account Name:',
        validators=[
            DataRequired(),
            account_exists,
        ]
    )
    balance = DecimalField(
        'Balance:',
        validators=[
            DataRequired(),
        ],
        places=2,
        rounding=False,
    )
    accnt_type = SelectField(
        u'Account Type:',
        choices=[
            ('checking', 'CHECKING'),
            ('savings', 'SAVINGS')
        ]
    )
    bank = StringField(
        'Associated Bank:',
        validators=[
            DataRequired(),
        ]
    )


class CreateEntryForm(FlaskForm):
    descrip = StringField(
        "Description:",
        validators=[
            DataRequired(),
        ]
    )
    date = DateField(
        "Date (YYYY-MM-DD):",
        validators=[
            DataRequired(),
        ]
    )
    tranact_type = SelectField(
        "Transaction Type:",
        choices=[
            ('debit', 'DEBIT'),
            ('credit', 'CREDIT'),
        ]
    )
    amount = DecimalField(
        'Amount:',
        validators=[
            DataRequired(),
        ],
        places=2,
        rounding=False,
    )
    # assc_accnt choices are append to the form
    # at the time of the request.
    assc_accnt = SelectField(
        'Associated Account:'
    )

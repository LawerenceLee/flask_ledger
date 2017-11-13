from flask_wtf import FlaskForm
from wtforms import (DateField, DecimalField,
                     StringField, SelectField,
                     )
from wtforms.validators import (DataRequired, ValidationError)

from not_equal_validator import NotEqualTo
from models import Account


def account_exists(form, field):
    if Account.select().where(Account.name == field.data).exists():
        raise ValidationError('Account with that name already exists')


def must_be_positive(form, field):
    if field.data is None:
        pass
    elif field.data < 0:
        raise ValidationError('This value must be positive.')


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
            must_be_positive,
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
            must_be_positive,
        ],
        places=2,
        rounding=False,
    )
    # assc_accnt choices are appended to the form
    # at the time of the request.
    assc_accnt = SelectField(
        'Associated Account:'
    )


class CreateTransferForm(FlaskForm):
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
    amount = DecimalField(
        'Amount:',
        validators=[
            must_be_positive,
        ],
        places=2,
        rounding=False,
    )
    from_accnt = SelectField(
        'From Account:',
        validators=[
            DataRequired(),
            NotEqualTo('to_accnt', message='Accounts must be different')
        ]
    )
    to_accnt = SelectField(
        'To Account:',
        validators=[
            DataRequired(),
        ]
    )
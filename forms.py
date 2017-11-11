from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, TextAreaField
from wtforms.validators import (DataRequired, ValidationError)


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

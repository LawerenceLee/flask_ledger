from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError)

from models import Account, Entry, Transfer


def name_exists(form, field):
        if Account.select().where(Account.name == field.data).exists():
            raise ValidationError('Account with that name already exists.')


class CreateAccountForm(FlaskForm):
    name = StringField(
        'Account Name: ',
        validators=[
            DataRequired(),
            name_exists,
        ]
    )
    balance = DecimalField(places=2, rounding=None)
    accnt_type = SelectField(
        u'Account Type',
        choices=[
            ('debit', 'DEBIT'),
            ('checking', 'CHECKING')
        ]
    )
    bank = StringField(
        'Bank',
        validators=[
            DataRequired,
        ]
    )

#  CREATE INDEX PAGE NEXT, THEN ACCOUNT CREATION PAGE

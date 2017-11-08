from peewee import (CharField, DateField, DecimalField,
                    ForeignKeyField, IntegrityError, Model,
                    SqliteDatabase, )

DATABASE = SqliteDatabase('ledger.db', threadlocals=True)


class Account(Model):
    name = CharField(max_length=50, unique=True)
    balance = DecimalField(decimal_places=2, auto_round=False)
    accnt_type = CharField()
    bank = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_account(cls, name, balance, accnt_type, bank):
        try:
            with DATABASE.transaction():
                cls.create(
                    name=name,
                    balance=balance,
                    accnt_type=accnt_type,
                    bank=bank,
                )
        except IntegrityError:
            raise ValueError('Account Already Exists')

    def debit(self, amount):
        self.balance = self.balance - amount

    def credit(self, amount):
        self.balance = self.balance + amount


class Entry(Model):
    descrip = CharField()
    date = DateField()
    tranact_type = CharField()
    amount = DecimalField(decimal_places=2, auto_round=False)

    assc_accnt = ForeignKeyField(
        rel_model=Account,
        related_name='entries',
    )

    class Meta():
        database = DATABASE
        order_by = ('-date',)

    def mk_accnt_chgs(self):
        if self.tranact_type == 'debit':
            self.assc_accnt.debit(self.amount)
        elif self.tranact_type == 'credit':
            self.assc_accnt.credit(self.amount)
        else:
            raise ValueError('Transaction Type can only be Credit or Debit.')


class Transfer(Model):
    descrip = CharField()
    date = DateField()
    amount = DecimalField(decimal_places=2, auto_round=False)
    from_accnt = ForeignKeyField(
        rel_model=Account,
        related_name='from_accnts'
    )
    to_accnt = ForeignKeyField(
        rel_model=Account,
        related_name='to_accnts'
    )

    class Meta():
        database = DATABASE
        order_by = ('-date',)

    def mk_transfer(self):
        self.from_accnt.debit(amount=self.amount)
        self.to_accnt.credit(amount=self.amount)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Account, Entry, Transfer], safe=True)
    DATABASE.close()

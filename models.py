from peewee import (CharField, Check, DateField, FloatField,
                    ForeignKeyField, IntegrityError, Model,
                    SqliteDatabase, )

DATABASE = SqliteDatabase('ledger.db', threadlocals=True)


class Account(Model):
    name = CharField(max_length=50, unique=True)
    balance = FloatField()
    # Account Type
    accnt_type = CharField()
    bank = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_account(cls, name, balance, accnt_type, bank):
        """Creates accounts using peewee's built-in
        transaction method. If an exception occurs
        within the DATABASE.transaction() block, the transaction will
        be rolled back. Otherwise the statements will be committed at
        the end of the block.
        - Peewee Docs
        """
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

    def __repr__(self):
        return "Account.create_account(name='{}', balance={}, accnt_type='{}', bank='{}')".format(
                    self.name, self.balance, self.accnt_type, self.bank
                )

    def __str__(self):
        return "Name: {}, Balance: ${}".format(self.name, self.balance)

    @staticmethod
    def debit(accnt_name, accnt_balance, amount):
        """Subtracts a specified amount from an account"""
        Account.update(
            balance=accnt_balance-amount).where(
                Account.name == accnt_name).execute()

    @staticmethod
    def credit(accnt_name, accnt_balance, amount):
        """Adds a specified amount to an account"""
        Account.update(
            balance=accnt_balance+amount).where(
                Account.name == accnt_name).execute()


class Entry(Model):
    # Description
    descrip = CharField()
    date = DateField()
    # Transaction Type
    tranact_type = CharField(
        constraints=[Check(
            "tranact_type == 'debit' or tranact_type == 'credit'"
        )])
    amount = FloatField(
        constraints=[Check("amount >= 0")]
        )
    # Associated Account
    assc_accnt = ForeignKeyField(
        rel_model=Account,
        related_name='entries',
    )

    class Meta():
        database = DATABASE
        order_by = ('-date',)

    @classmethod
    def create_entry(cls, descrip, date, tranact_type, amount, assc_accnt):
        """Creates entries using peewee's built-in
        transaction method. Essentially, if an exception occurs
        within the DATABASE.transaction() block, the transaction will
        be rolled back. Otherwise the statements will be committed at
        the end of the block.
        - Peewee Docs
        """
        with DATABASE.transaction():
            cls.create(
                descrip=descrip,
                date=date,
                tranact_type=tranact_type,
                amount=amount,
                assc_accnt=assc_accnt,
            )

    def __repr__(self):
        return """Entry.create_entry(descrip='{}', date={}, tranact_type='{}', amount={}, assc_accnt={})
               """.format(
                       self.descrip, self.date, self.tranact_type,
                       self.amount, self.assc_accnt
                   )

    def __str__(self):
        return "Description: {}, Amount: ${}".format(self.descrip, self.amount)

    def mk_accnt_chgs(self):
        if self.tranact_type == 'debit':
            self.assc_accnt.debit(
                self.assc_accnt.name,
                self.assc_accnt.balance,
                self.amount
            )
        elif self.tranact_type == 'credit':
            self.assc_accnt.credit(
                self.assc_accnt.name,
                self.assc_accnt.balance,
                self.amount
            )


class Transfer(Model):
    """Facilitates the transfer of funds from one account to another."""
    # Description
    descrip = CharField()
    date = DateField()
    amount = FloatField(
        constraints=[Check("amount >= 0")]
        )
    # From Account
    from_accnt = ForeignKeyField(
        rel_model=Account,
        related_name='from_accnts'
    )
    # To Account
    to_accnt = ForeignKeyField(
        rel_model=Account,
        related_name='to_accnts'
    )

    class Meta():
        database = DATABASE
        order_by = ('-date',)

    @classmethod
    def create_transfer(cls, descrip, date, amount, from_accnt, to_accnt):
        with DATABASE.transaction():
            cls.create(
                descrip=descrip,
                date=date,
                amount=amount,
                from_accnt=from_accnt,
                to_accnt=to_accnt,
            )

    def __repr__(self):
        return """Transfer.create_transfer(descrip='{}', date={}, amount={}, from_accnt={}, to_accnt={})
               """.format(
                        self.descrip, self.date, self.amount, self.from_accnt,
                        self.to_accnt
                    )

    def __str__(self):
        return "From Account: {}, To Account: {}, Amount: ${}".format(
                    self.from_accnt.name, self.to_accnt.name, self.amount)

    def mk_transfer(self):
        """Deducts the transfer's amount from the 'from_accnt', and
        adds it to the 'to_accnt'.
        """
        self.from_accnt.debit(
            self.from_accnt.name,
            self.from_accnt.balance,
            self.amount)
        self.to_accnt.credit(
            self.to_accnt.name,
            self.to_accnt.balance,
            self.amount)


def initialize():
    """Makes a connection to the ledger.db database, creates the
    neccessary tables if they do not exist, and promptly closes the
    connection
    """
    DATABASE.connect()
    DATABASE.create_tables([Account, Entry, Transfer], safe=True)
    DATABASE.close()

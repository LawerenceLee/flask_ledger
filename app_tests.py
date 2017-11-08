import os
import unittest

from playhouse.test_utils import test_database
from peewee import IntegrityError, SqliteDatabase

import flask_ledger
from models import (Account, Entry, Transfer)

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Account, ], safe=True)


class AccountModelTestCase(unittest.TestCase):

    @staticmethod
    def create_accounts(count=2):
        """Creates two accounts for testing purposes."""
        for i in range(count):
            Account.create_account(
                name='Checking Account #{}'.format(i),
                balance=1000,
                accnt_type='Checking',
                bank='Chase',
            )

    def test_create_account(self):
        """Tests the creation of two accounts."""
        with test_database(TEST_DB, (Account, )):

            # Create 2 accounts, and check if in database.
            self.create_accounts()
            self.assertEqual(Account.select().count(), 2)

    def test_duplicate_account(self):
        """Tests if a ValueError is raised upon the attempted
        creation of an account with a name matching one that
        already resides in the database.
        """
        with test_database(TEST_DB, (Account, )):

            # Creates an account with the name:
            # 'Checking Account #0'
            self.create_accounts(1)

            # Check if a ValueError is raised upon
            # creating a duplicate account.
            with self.assertRaises(ValueError):
                Account.create_account(
                    name='Checking Account #0',
                    balance=1000,
                    accnt_type='checking',
                    bank='Chase',
                )


class EntryModelTestCase(unittest.TestCase):

    @staticmethod
    def create_entries(account):
        """Create two entries, one credit, one debit for
        testing purposes.
        """
        Entry.create_entry(
            descrip='Car Repair',
            date='09/05/1961',
            tranact_type='debit',
            amount=500,
            assc_accnt=account,
        )
        Entry.create_entry(
                descrip='Paycheck',
                date='09/05/1961',
                tranact_type='credit',
                amount=500,
                assc_accnt=account,
            )

    def test_entry_creation(self):
        with test_database(TEST_DB, (Account, Entry)):
            """Tests the creation of entries in the database."""
            # Create account & save to variable.
            AccountModelTestCase.create_accounts()
            account = Account.select().get()

            # Create two entries & save one to a variable.
            self.create_entries(account=account)
            entry = Entry.select().get()

            # Check if entries are in database.
            self.assertEqual(Entry.select().count(), 2)
            # Does the account assigned as a foreign key
            # to entry match the one provided to the create_entries
            # method.
            self.assertEqual(entry.assc_accnt, account)

    def test_bad_mk_accnt_chgs(self):
        with test_database(TEST_DB, (Account, Entry)):
            """Tests if a ValueError is raised when instantiating
            an instance of the Entry class with a 'tranact_type'
            other that 'debit', or 'credit'.
            """
            # Create an account & assign it to a variable.
            AccountModelTestCase.create_accounts(1)
            account = Account.select().get()

            # Assert if a ValueError was raised.
            # Create an Entry instance w/ bad tranact_type.
            with self.assertRaises(IntegrityError):
                Entry.create_entry(
                    descrip='Paycheck',
                    date='09/05/1961',
                    tranact_type='gibberish',
                    amount=500,
                    assc_accnt=account,
                )


class DebitCreditTestCase(unittest.TestCase):

    def test_debit_credit_functions(self):
        """Tests that the create_entry method accurately
        debits or credits money to an account specified within
        an Entry class instance.
        """
        with test_database(TEST_DB, (Account, Entry)):
            # Create two accounts & assign both two variables.
            AccountModelTestCase.create_accounts()
            account_1 = Account.select().where(Account.id == 1).get()
            account_2 = Account.select().where(Account.id == 2).get()

            # Create an entry for each account, one debit, one
            # credit, & assign both to variables.
            EntryModelTestCase.create_entries(account=account_1)
            EntryModelTestCase.create_entries(account=account_2)
            entry_1 = Entry.select().where(Entry.id == 1).get()
            entry_2 = Entry.select().where(Entry.id == 2).get()

            # Shift balances of accounts according to entries.
            entry_1.mk_accnt_chgs()
            entry_2.mk_accnt_chgs()

            # Assert that each account's new balance reflects the
            # changes in their corresponding entry.
            self.assertEqual(entry_1.assc_accnt.balance, 500.00)
            self.assertEqual(entry_2.assc_accnt.balance, 1500.00)


class TransferModelTestCase(unittest.TestCase):

    @staticmethod
    def create_transfers(from_accnt, to_accnt, count=2):
        """Creates two instances of the Transfer class
        to used in the following test/s.
        """
        for i in range(count):
            Transfer.create(
                descrip='Test Transfer {}'.format(i),
                date='09/05/1961',
                amount=50,
                from_accnt=from_accnt,
                to_accnt=to_accnt,
            )

    def test_transfer_creation(self):
        """Creates two test accounts, deducts an amount
        from one account and adds it to the other,
        checks if the accounts balances reflect the
        changes specified in the Transfer.
        """
        with test_database(TEST_DB, (Account, Transfer)):
            # Two accounts created
            AccountModelTestCase.create_accounts()
            account_1 = Account.select().where(Account.id == 1).get()
            account_2 = Account.select().where(Account.id == 2).get()

            # Create a Transfer instance (does not
            # actually perform transfer, merely a
            # record), retrieve it from database,
            # assign to variable.
            self.create_transfers(account_1, account_2)
            transfer = Transfer.select().get()  # Get 1st record.

            # Shifts funds between accounts.
            transfer.mk_transfer()

            # Checks if balances reflect changes
            # specified in Transfer instance.
            self.assertEqual(transfer.from_accnt.balance, 950)
            self.assertEqual(transfer.to_accnt.balance, 1050)


class ViewTestCase(unittest.TestCase):

    def setUp(self):
        """Creates a new test client. TESTING flag
        disables the error catching during request
        handling so that you get better error reports
        when performing test requests against the
        application.
        - Flask Testing Docs

        Setting WTF_CSRF_ENABLED to False turns off
        the generation of CSRF Tokens for requests.
        - Flask WTF Docs
        """
        flask_ledger.app.config['TESTING'] = True
        flask_ledger.app.config['WTF_CSRF_ENABLED'] = False
        self.app = flask_ledger.app.test_client()


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    unittest.main()

import os
import unittest

from playhouse.test_utils import test_database
from peewee import IntegrityError, SqliteDatabase

import flask_ledger
from models import Account, Entry, Transfer

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Account, Entry, Transfer], safe=True)


class AccountModelTestCase(unittest.TestCase):

    @staticmethod
    def create_accounts(count=2):
        """Creates two accounts for testing purposes."""
        for i in range(count):
            Account.create_account(
                name='Checking Account #{}'.format(i),
                balance=1000,
                accnt_type='checking',
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

    def test_repr_method(self):
        with test_database(TEST_DB, (Account, )):
            self.create_accounts(1)
            account_1 = Account.select().get()

            instance = "Account.create_account(name='Checking Account #0', balance=1000.0, accnt_type='checking', bank='Chase')"

            self.assertEqual(instance, repr(account_1))

    def test_str_method(self):
        with test_database(TEST_DB, (Account, )):
            self.create_accounts(1)
            account_1 = Account.select().get()

            str_var = "Name: Checking Account #0, Balance: $1000.0"

            self.assertEqual(str_var, str(account_1))


class EntryModelTestCase(unittest.TestCase):

    @staticmethod
    def create_entries(account, tranact_type, count=2):
        """Create two entries, one credit, one debit for
        testing purposes.
        """
        for i in range(count):
            Entry.create_entry(
                descrip='Car Repair',
                date='09/05/1961',
                tranact_type=tranact_type,
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
            self.create_entries(account, 'debit')
            entry = Entry.select().get()

            # Check if entries are in database.
            self.assertEqual(Entry.select().count(), 2)
            # Does the account assigned as a foreign key
            # to entry match the one provided to the create_entries
            # method.
            self.assertEqual(entry.assc_accnt, account)

    def test_bad_tranact_type(self):
        with test_database(TEST_DB, (Account, Entry)):
            """Tests if a peewee.IntegrityError is raised when instantiating
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

    def test_bad_amount(self):
        with test_database(TEST_DB, (Account, Entry)):
            """Tests if a peewee.IntegrityError is raised when instantiating
            an instance of the Entry class with an 'amount'
            that is negative.
            """
            AccountModelTestCase.create_accounts(1)
            account = Account.select().get()

            with self.assertRaises(IntegrityError):
                Entry.create_entry(
                    descrip='Paycheck',
                    date='09/05/1961',
                    tranact_type='gibberish',
                    amount=-500,
                    assc_accnt=account,
                )

    def test_str_method(self):
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts(1)
            account_1 = Account.select().get()
            self.create_entries(account_1, 'credit', 1)
            entry = Entry.select().get()

            str_var = "Description: Car Repair, Amount: $500.0"

            self.assertEqual(str_var, str(entry))


class DebitCreditTestCase(unittest.TestCase):

    def test_debit_credit_functions(self):
        """Tests that the create_entry method accurately
        debits or credits money to an account specified within
        an Entry class instance.
        """
        with test_database(TEST_DB, (Account, Entry)):
            # Create two accounts & assign both two variables.
            AccountModelTestCase.create_accounts(2)
            account_1 = Account.select().where(Account.id == 1).get()
            account_2 = Account.select().where(Account.id == 2).get()

            # Create an entry for each account, one debit, one
            # credit, & assign both to variables.
            EntryModelTestCase.create_entries(account_1, 'debit', 1)
            EntryModelTestCase.create_entries(account_2, 'credit', 1)
            entry_1 = Entry.select().where(Entry.id == 1).get()
            entry_2 = Entry.select().where(Entry.id == 2).get()

            # Shift balances of accounts according to entries.
            entry_1.mk_accnt_chgs()
            entry_2.mk_accnt_chgs()

            account_1_update = Account.select().where(Account.id == 1).get()
            account_2_update = Account.select().where(Account.id == 2).get()

            # Assert that each account's new balance reflects the
            # changes in their corresponding entry.
            self.assertEqual(account_1_update.balance, 500.00)
            self.assertEqual(account_2_update.balance, 1500.00)


class TransferModelTestCase(unittest.TestCase):

    @staticmethod
    def create_transfers(from_accnt, to_accnt, count=2):
        """Creates two instances of the Transfer class
        to used in the following test/s.
        """
        for i in range(count):
            Transfer.create_transfer(
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
            AccountModelTestCase.create_accounts()
            from_account = Account.select().where(Account.id == 1).get()
            to_account = Account.select().where(Account.id == 2).get()

            # Create a Transfer instance (does not
            # actually perform transfer, merely a
            # record), retrieve it from database,
            # assign to variable.
            self.create_transfers(from_account, to_account)
            transfer = Transfer.select().get()

            # Shifts funds between accounts.
            transfer.mk_transfer()

            from_account_update = Account.select().where(Account.id == 1).get()
            to_account_update = Account.select().where(Account.id == 2).get()

            # Checks if balances reflect changes
            # specified in Transfer instance.
            self.assertEqual(from_account_update.balance, 950)
            self.assertEqual(to_account_update.balance, 1050)

    def test_bad_amount(self):
        """Tests if a peewee.IntegrityError is raised when
        instantiating an instance of the Transfer class with
        an 'amount' that is negative.
        """
        with test_database(TEST_DB, (Account, Transfer)):
            AccountModelTestCase.create_accounts()
            account_1 = Account.select().where(Account.id == 1).get()
            account_2 = Account.select().where(Account.id == 2).get()

            with self.assertRaises(IntegrityError):
                Transfer.create_transfer(
                    descrip='Test Transfer',
                    date='09/05/1961',
                    amount=-50,
                    from_accnt=account_1,
                    to_accnt=account_2,
                )

    def test_str_method(self):
        with test_database(TEST_DB, (Account, Transfer)):
            AccountModelTestCase.create_accounts()
            to_account = Account.select().where(Account.id == 1).get()
            from_account = Account.select().where(Account.id == 2).get()

            self.create_transfers(from_account, to_account, 1)
            transfer = Transfer.select().get()

            str_var = "From Account: Checking Account #1, To Account: Checking Account #0, Amount: $50.0"

            self.assertEqual(str(transfer), str_var)


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


class IndexViewTestCase(ViewTestCase):
    '''Inherits from ViewTestCase'''

    def test_empty_database(self):
        with test_database(TEST_DB, (Account, )):
            rv = self.app.get('/')
            self.assertIn(
                "no accounts yet", rv.get_data(as_text=True).lower()
                )

    def test_accnts_list(self):
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts(1)
            rv = self.app.get('/')
            self.assertIn(
                'checking account #0', rv.get_data(
                    as_text=True).lower()
                )
            self.assertIn(
                'no entries for this account yet', rv.get_data(
                    as_text=True).lower()
                )
            self.assertNotIn(
                "no accounts yet", rv.get_data(
                    as_text=True).lower()
                )

    def test_list_of_entries_for_accnts(self):
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts(2)
            account_1 = Account.select().where(Account.id == 1).get()
            account_2 = Account.select().where(Account.id == 1).get()
            EntryModelTestCase.create_entries(account_1, 'credit', 1)
            EntryModelTestCase.create_entries(account_2, 'debit', 1)
            entry_1 = Entry.select().where(Entry.id == 1).get()
            entry_2 = Entry.select().where(Entry.id == 2).get()
            rv = self.app.get('/')
            self.assertIn(
                account_1.name, rv.get_data(
                    as_text=True)
                )
            self.assertIn(
                account_2.name, rv.get_data(
                    as_text=True)
                )
            self.assertIn(
                entry_1.descrip, rv.get_data(
                    as_text=True)
                )
            self.assertIn(
                entry_2.descrip, rv.get_data(
                    as_text=True)
                )
            self.assertNotIn(
                "no accounts yet", rv.get_data(
                    as_text=True).lower()
                )


class CreateAccountViewTestCase(ViewTestCase):
    '''Inherits from ViewTestCase'''

    def test_create_accnt(self):
        account_data = {
            'name': 'Checking Account',
            'balance': 1000,
            'accnt_type': 'checking',
            'bank': 'Chase',
        }
        with test_database(TEST_DB, (Account, )):
            rv = self.app.post('/create_account', data=account_data)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')
            self.assertEqual(Account.select().count(), 1)

    def test_duplicate_accnt(self):
        account_data = {
            'name': 'Checking Account #0',
            'balance': 1000,
            'accnt_type': 'checking',
            'bank': 'Chase',
        }
        with test_database(TEST_DB, (Account, )):
            AccountModelTestCase.create_accounts(1)
            rv = self.app.post('/create_account', data=account_data)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(
                'Account with that name already exists',
                rv.get_data(as_text=True))
            self.assertEqual(Account.select().count(), 1)

    def test_bad_balance_for_accnt(self):
        account_data = {
            'name': 'Checking Account',
            'balance': -1000,
            'accnt_type': 'checking',
            'bank': 'Chase',
        }
        with test_database(TEST_DB, (Account, )):
            rv = self.app.post('/create_account', data=account_data)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(
                'This value must be positive.', rv.get_data(as_text=True)
            )
            self.assertEqual(Account.select().count(), 0)


class CreateEntryViewTestCase(ViewTestCase):
    '''Inherits from ViewTestCase'''

    def test_create_entry(self):
        entry_data = {
            'descrip': 'Passing Go',
            'date': '2017-11-12',
            'tranact_type': 'credit',
            'amount': 50,
            'assc_accnt': 1,
        }
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts(1)
            rv = self.app.post('/create_entry', data=entry_data)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')
            self.assertEqual(Entry.select().count(), 1)

    def test_create_entry_without_accnt(self):
        with test_database(TEST_DB, (Account, Entry)):
            rv = self.app.get('/create_entry')
            self.assertEqual(Entry.select().count(), 0)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_bad_amount_for_entry(self):
        entry_data = {
            'descrip': 'Passing Go',
            'date': '2017-11-12',
            'tranact_type': 'credit',
            'amount': -50,
            'assc_accnt': 1,
        }
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts(1)
            rv = self.app.post('/create_entry', data=entry_data)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(
                'This value must be positive.', rv.get_data(as_text=True)
            )
            self.assertEqual(Entry.select().count(), 0)


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    unittest.main()

import os
import unittest

from playhouse.test_utils import test_database
from peewee import SqliteDatabase

# import flask_ledger
from models import (Account, Entry, Transfer)

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Account, ], safe=True)


class AccountModelTestCase(unittest.TestCase):

    @staticmethod
    def create_accounts(count=2):
        for i in range(count):
            Account.create_account(
                name='Checking Account #{}'.format(i),
                balance=1000 + i,
                accnt_type='Checking',
                bank='Chase',
            )

    def test_create_account(self):
        with test_database(TEST_DB, (Account, )):
            self.create_accounts()
            self.assertEqual(Account.select().count(), 2)

    def test_duplicate_account(self):
        with test_database(TEST_DB, (Account, )):
            self.create_accounts()
            with self.assertRaises(ValueError):
                Account.create_account(
                    name='Checking Account #1',
                    balance=1000,
                    accnt_type='checking',
                    bank='Chase',
                )


class EntryModelTestCase(unittest.TestCase):

    @staticmethod
    def create_entries(account):
        Entry.create(
            descrip='Car Repair',
            date='09/05/1961',
            tranact_type='debit',
            amount='500',
            assc_accnt=account,
        )
        Entry.create(
                descrip='Paycheck',
                date='09/05/1961',
                tranact_type='credit',
                amount='500',
                assc_accnt=account,
            )

    def test_entry_creation(self):
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts()
            account = Account.select().get()

            self.create_entries(account=account)
            entry = Entry.select().get()

            self.assertEqual(Entry.select().count(), 2)
            self.assertEqual(entry.assc_accnt, account)

    def test_bad_mk_accnt_chgs(self):
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts()
            account = Account.select().get()

            Entry.create(
                descrip='Paycheck',
                date='09/05/1961',
                tranact_type='gibberish',
                amount='500',
                assc_accnt=account,
            )
            entry = Entry.select().get()

            with self.assertRaises(ValueError):
                entry.mk_accnt_chgs()


class DebitCreditTestCase(unittest.TestCase):

    def test_debit_credit_functions(self):
        with test_database(TEST_DB, (Account, Entry)):
            AccountModelTestCase.create_accounts()
            account_1 = Account.select().where(Account.id == 1).get()
            account_2 = Account.select().where(Account.id == 2).get()

            EntryModelTestCase.create_entries(account=account_1)
            EntryModelTestCase.create_entries(account=account_2)
            entry_1 = Entry.select().where(Entry.id == 1).get()
            entry_2 = Entry.select().where(Entry.id == 2).get()

            entry_1.mk_accnt_chgs()
            entry_2.mk_accnt_chgs()

            self.assertEqual(entry_1.assc_accnt.balance, 500.00)
            self.assertEqual(entry_2.assc_accnt.balance, 1500.00)


class TransferModelTestCase(unittest.TestCase):

    @staticmethod
    def create_transfers(from_accnt, to_accnt, count=2):
        for i in range(count):
            Transfer.create(
                descrip='Test Transfer {}'.format(i),
                date='09/05/1961',
                amount=50,
                from_accnt=from_accnt,
                to_accnt=to_accnt,
            )

    def test_transfer_creation(self):
        with test_database(TEST_DB, (Account, Transfer)):
            AccountModelTestCase.create_accounts()
            account_1 = Account.select().where(Account.id == 1).get()
            account_2 = Account.select().where(Account.id == 2).get()

            self.create_transfers(account_1, account_2)
            transfer = Transfer.select().get()

            transfer.mk_transfer()

            self.assertEqual(transfer.from_accnt.balance, 950)
            self.assertEqual(transfer.to_accnt.balance, 1051)


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    unittest.main()

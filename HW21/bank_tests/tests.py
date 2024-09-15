import unittest
from bank_account import BankAccount, InsufficientFunds

class TestBankAccount(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(100)
        self.other_account = BankAccount(50)

    def test_deposit_positive_amount(self):
        self.account.deposit(50)
        self.assertEqual(self.account.get_balance(), 150)

    def test_deposit_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-50)

    def test_deposit_zero(self):
        with self.assertRaises(ValueError):
            self.account.deposit(0)

    def test_withdraw_valid_amount(self):
        self.account.withdraw(50)
        self.assertEqual(self.account.get_balance(), 50)

    def test_withdraw_more_than_balance(self):
        with self.assertRaises(InsufficientFunds):
            self.account.withdraw(200)

    def test_withdraw_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(-10)

    def test_withdraw_zero(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(0)

    def test_transfer_valid_amount(self):
        self.account.transfer(self.other_account, 50)
        self.assertEqual(self.account.get_balance(), 50)
        self.assertEqual(self.other_account.get_balance(), 100)

    def test_transfer_more_than_balance(self):
        with self.assertRaises(InsufficientFunds):
            self.account.transfer(self.other_account, 200)

    def test_transfer_invalid_account(self):
        with self.assertRaises(TypeError):
            self.account.transfer("Not a bank account", 50)

    def test_transfer_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.transfer(self.other_account, -10)

    def test_get_balance(self):
        self.assertEqual(self.account.get_balance(), 100)

if __name__ == '__main__':
    unittest.main()

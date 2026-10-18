import unittest
from balance.balance import Balance
from balance.balance_decorators import (
    LoggingBalanceDecorator, ValidatingBalanceDecorator)
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestBalanceDecorators(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_validating_passes_good_transaction(self):
        wrapped = ValidatingBalanceDecorator(self.balance)
        wrapped.apply_transaction(Transaction(40, TransactionCategory.INCOME))
        self.assertEqual(self.balance.get_balance(), 40)

    def test_validating_rejects_zero_and_negative(self):
        wrapped = ValidatingBalanceDecorator(self.balance)
        for amount in (0, -5):
            with self.assertRaises(ValueError):
                wrapped.apply_transaction(Transaction(amount, TransactionCategory.INCOME))
        self.assertEqual(self.balance.get_balance(), 0)

    def test_validating_rejects_non_numbers(self):
        wrapped = ValidatingBalanceDecorator(self.balance)
        for amount in ("100", None, True):
            with self.assertRaises(ValueError):
                wrapped.apply_transaction(Transaction(amount, TransactionCategory.INCOME))

    def test_validating_rejects_bad_category(self):
        wrapped = ValidatingBalanceDecorator(self.balance)
        with self.assertRaises(ValueError):
            wrapped.apply_transaction(Transaction(10, "income"))

    def test_other_methods_are_forwarded(self):
        wrapped = ValidatingBalanceDecorator(self.balance)
        self.balance.add_income(5)
        self.assertEqual(wrapped.get_balance(), 5)

    def test_logging_logs_success(self):
        wrapped = LoggingBalanceDecorator(self.balance)
        with self.assertLogs("finance", level="INFO") as logs:
            wrapped.apply_transaction(Transaction(40, TransactionCategory.INCOME))
        self.assertEqual(len(logs.output), 2)
        self.assertEqual(self.balance.get_balance(), 40)

    def test_logging_logs_rejection(self):
        wrapped = LoggingBalanceDecorator(
            ValidatingBalanceDecorator(self.balance))
        with self.assertLogs("finance", level="WARNING") as logs:
            with self.assertRaises(ValueError):
                wrapped.apply_transaction(Transaction(-1, TransactionCategory.INCOME))
        self.assertIn("Rejected", logs.output[0])


if __name__ == "__main__":
    unittest.main()

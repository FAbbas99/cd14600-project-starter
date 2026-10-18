import unittest
from unittest.mock import patch
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from balance.balance import Balance
from balance.balance_observer import (
    IBalanceObserver, LowBalanceAlertObserver, PrintObserver)


class TestLowBalanceAlertObserver(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_alert_triggers_on_low_balance(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

    def test_print_observer_prints_on_change(self):
        self.balance.register_observer(PrintObserver())
        with patch("builtins.print") as mock_print:
            self.balance.apply_transaction(
                Transaction(10, TransactionCategory.INCOME))
        mock_print.assert_called_once()
        self.assertIn("10", mock_print.call_args[0][0])

    def test_removed_observer_not_notified(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)
        self.balance.remove_observer(observer)
        self.balance.apply_transaction(
            Transaction(10, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

    def test_base_observer_requires_update(self):
        with self.assertRaises(NotImplementedError):
            IBalanceObserver().update(self.balance, None)


if __name__ == "__main__":
    unittest.main()

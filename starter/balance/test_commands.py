import unittest
from balance.balance import Balance
from balance.commands import ApplyTransactionCommand, CommandHistory
from balance.overdraft_policy import NoOverdraft
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.history = CommandHistory()

    def _cmd(self, amount, category):
        return ApplyTransactionCommand(
            self.balance, Transaction(amount, category))

    def test_execute_applies_transaction(self):
        self.history.execute(self._cmd(100, TransactionCategory.INCOME))
        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_income(self):
        self.history.execute(self._cmd(100, TransactionCategory.INCOME))
        self.assertTrue(self.history.undo())
        self.assertEqual(self.balance.get_balance(), 0)

    def test_undo_expense(self):
        self.history.execute(self._cmd(100, TransactionCategory.INCOME))
        self.history.execute(self._cmd(30, TransactionCategory.EXPENSE))
        self.history.undo()
        self.assertEqual(self.balance.get_balance(), 100)

    def test_redo(self):
        self.history.execute(self._cmd(100, TransactionCategory.INCOME))
        self.history.undo()
        self.assertTrue(self.history.redo())
        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_and_redo_with_empty_history(self):
        self.assertFalse(self.history.undo())
        self.assertFalse(self.history.redo())

    def test_new_command_clears_redo(self):
        self.history.execute(self._cmd(100, TransactionCategory.INCOME))
        self.history.undo()
        self.history.execute(self._cmd(10, TransactionCategory.INCOME))
        self.assertFalse(self.history.redo())

    def test_failed_command_is_not_recorded(self):
        self.balance.set_overdraft_policy(NoOverdraft())
        with self.assertRaises(ValueError):
            self.history.execute(self._cmd(10, TransactionCategory.EXPENSE))
        self.assertFalse(self.history.undo())

    def test_undo_notifies_observers(self):
        seen = []

        class Spy:
            def update(self, balance, transaction):
                seen.append(transaction)

        self.balance.register_observer(Spy())
        self.history.execute(self._cmd(50, TransactionCategory.EXPENSE))
        self.history.undo()
        self.assertEqual(seen[-1], Transaction(50, TransactionCategory.INCOME))

    def test_base_command_requires_methods(self):
        from balance.commands import ICommand
        with self.assertRaises(NotImplementedError):
            ICommand().execute()
        with self.assertRaises(NotImplementedError):
            ICommand().undo()


if __name__ == "__main__":
    unittest.main()

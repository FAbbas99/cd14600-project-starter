import unittest
from balance.balance import Balance
from balance.overdraft_policy import NoOverdraft, OverdraftLimit, AllowOverdraft
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestOverdraftPolicy(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_default_allows_overdraft(self):
        self.balance.add_expense(10)
        self.assertEqual(self.balance.get_balance(), -10)

    def test_no_overdraft_rejects_expense(self):
        self.balance.set_overdraft_policy(NoOverdraft())
        self.balance.add_income(50)
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(Transaction(80, TransactionCategory.EXPENSE))
        self.assertEqual(self.balance.get_balance(), 50)

    def test_no_overdraft_allows_exact_zero(self):
        self.balance.set_overdraft_policy(NoOverdraft())
        self.balance.add_income(50)
        self.balance.add_expense(50)
        self.assertEqual(self.balance.get_balance(), 0)

    def test_overdraft_limit(self):
        self.balance.set_overdraft_policy(OverdraftLimit(100))
        self.balance.add_expense(100)
        with self.assertRaises(ValueError):
            self.balance.add_expense(1)

    def test_policy_can_be_swapped(self):
        self.balance.set_overdraft_policy(NoOverdraft())
        self.balance.set_overdraft_policy(AllowOverdraft())
        self.balance.add_expense(5)
        self.assertEqual(self.balance.get_balance(), -5)

    def test_reset_restores_default_policy(self):
        self.balance.set_overdraft_policy(NoOverdraft())
        self.balance.reset()
        self.balance.add_expense(5)
        self.assertEqual(self.balance.get_balance(), -5)


if __name__ == "__main__":
    unittest.main()

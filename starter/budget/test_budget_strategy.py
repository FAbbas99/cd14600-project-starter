import unittest
from budget.budget_strategy import (
    BudgetPlanner, FiftyThirtyTwentyStrategy, IBudgetStrategy,
    ZeroBasedStrategy)


class TestBudgetStrategy(unittest.TestCase):

    def test_fifty_thirty_twenty(self):
        plan = BudgetPlanner(FiftyThirtyTwentyStrategy()).plan(1000)
        self.assertEqual(plan, {"Needs": 500, "Wants": 300, "Savings": 200})

    def test_zero_based_assigns_everything(self):
        strategy = ZeroBasedStrategy({"Rent": 600, "Food": 300, "Fun": 100})
        plan = BudgetPlanner(strategy).plan(1000)
        self.assertEqual(plan["Unassigned"], 0)

    def test_zero_based_shows_leftover(self):
        strategy = ZeroBasedStrategy({"Rent": 600})
        self.assertEqual(BudgetPlanner(strategy).plan(1000)["Unassigned"], 400)

    def test_zero_based_over_budget(self):
        strategy = ZeroBasedStrategy({"Rent": 1200})
        with self.assertRaises(ValueError):
            BudgetPlanner(strategy).plan(1000)

    def test_strategy_can_be_swapped(self):
        planner = BudgetPlanner(FiftyThirtyTwentyStrategy())
        planner.set_strategy(ZeroBasedStrategy({"Rent": 1000}))
        self.assertEqual(planner.plan(1000), {"Rent": 1000, "Unassigned": 0})

    def test_negative_income_rejected(self):
        with self.assertRaises(ValueError):
            BudgetPlanner(FiftyThirtyTwentyStrategy()).plan(-1)

    def test_base_strategy_requires_allocate(self):
        with self.assertRaises(NotImplementedError):
            IBudgetStrategy().allocate(100)


if __name__ == "__main__":
    unittest.main()

# budget_strategy.py
# Strategy pattern: different ways to split income into a budget.


class IBudgetStrategy:
    def allocate(self, income):
        """Return a dict of {budget category: amount} for the given income."""
        raise NotImplementedError("Subclasses must implement allocate.")


class FiftyThirtyTwentyStrategy(IBudgetStrategy):
    """50% needs, 30% wants, 20% savings."""

    def allocate(self, income):
        return {
            "Needs": income * 0.50,
            "Wants": income * 0.30,
            "Savings": income * 0.20,
        }


class ZeroBasedStrategy(IBudgetStrategy):
    """Every dollar gets a job. The user picks the amounts, and whatever is
    left over is shown as 'Unassigned' (it should be zero)."""

    def __init__(self, planned):
        self.planned = dict(planned)

    def allocate(self, income):
        total = sum(self.planned.values())
        if total > income:
            raise ValueError("Planned spending is more than the income.")
        plan = dict(self.planned)
        plan["Unassigned"] = income - total
        return plan


class BudgetPlanner:
    """Uses whichever strategy it is given and lets you swap it later."""

    def __init__(self, strategy):
        self._strategy = strategy

    def set_strategy(self, strategy):
        self._strategy = strategy

    def plan(self, income):
        if income < 0:
            raise ValueError("Income cannot be negative.")
        return self._strategy.allocate(income)

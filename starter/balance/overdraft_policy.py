# overdraft_policy.py
# Strategy pattern: interchangeable rules for whether an expense is allowed.


class IOverdraftPolicy:
    def allows_expense(self, current_balance, amount):
        """Return True if an expense of `amount` is allowed."""
        raise NotImplementedError("Subclasses must implement allows_expense.")


class AllowOverdraft(IOverdraftPolicy):
    """Default policy: the balance can go negative."""

    def allows_expense(self, current_balance, amount):
        return True


class NoOverdraft(IOverdraftPolicy):
    """Reject any expense that would push the balance below zero."""

    def allows_expense(self, current_balance, amount):
        return current_balance - amount >= 0


class OverdraftLimit(IOverdraftPolicy):
    """Allow the balance to go negative, but not past a fixed limit."""

    def __init__(self, limit):
        self.limit = limit

    def allows_expense(self, current_balance, amount):
        return current_balance - amount >= -self.limit

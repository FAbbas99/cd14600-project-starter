# balance.py

from transaction.transaction_category import TransactionCategory
from balance.overdraft_policy import AllowOverdraft


class Balance:
    """Singleton to track the balance."""

    _instance = None

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if Balance._instance is not None:
            raise RuntimeError("Use Balance.get_instance() instead.")
        self._net_balance = 0.0
        self._observers = []
        self._overdraft_policy = AllowOverdraft()

    @classmethod
    def get_instance(cls):
        """Return the single Balance instance, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reset(self):
        """Reset the net balance to zero.

        Observers and the overdraft policy are reset too, so state from one
        run (or test) doesn't leak into the next.
        """
        self._net_balance = 0.0
        self._observers = []
        self._overdraft_policy = AllowOverdraft()

    def set_overdraft_policy(self, policy):
        """Inject the strategy used to decide if an expense is allowed."""
        self._overdraft_policy = policy

    def register_observer(self, observer):
        """Register an observer to be notified of balance changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """Stop notifying an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, transaction):
        for observer in list(self._observers):
            observer.update(self, transaction)

    def add_income(self, amount):
        """Add income to the balance."""
        self._net_balance += amount

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        if not self._overdraft_policy.allows_expense(self._net_balance, amount):
            raise ValueError("Expense rejected by overdraft policy.")
        self._net_balance -= amount

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance.

        Args:
            transaction (Transaction): The transaction to apply.
        """
        if transaction.category == TransactionCategory.INCOME:
            self.add_income(transaction.amount)
        elif transaction.category == TransactionCategory.EXPENSE:
            self.add_expense(transaction.amount)
        else:
            raise ValueError(f"Invalid transaction category: {transaction.category}")
        self._notify_observers(transaction)

    def get_balance(self):
        """Get the current net balance."""
        return self._net_balance

    def summary(self):
        """Return a summary string of the net balance."""
        return f"Net balance: ${self._net_balance}"

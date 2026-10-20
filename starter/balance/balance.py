# balance.py

from transaction.transaction_category import TransactionCategory
from transaction.transaction import Transaction
from balance.overdraft_policy import AllowOverdraft


class Balance:
    """Singleton to track the balance."""

    _instance = None

    def __new__(cls):
        """Create the one shared instance, or return it if it exists.

        Allocation is controlled here, so Balance() and get_instance()
        always give back the same object, even on the very first call.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Set up the state once. Later Balance() calls keep existing state.

        Python calls __init__ every time Balance() is called, so without
        this check a second call would wipe the balance. Use reset() to
        clear state on purpose.
        """
        if self._initialized:
            return
        self._initialized = True
        self._net_balance = 0.0
        self._observers = []
        self._overdraft_policy = AllowOverdraft()

    @classmethod
    def get_instance(cls):
        """Return the single Balance instance, creating it if needed."""
        return cls()

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
        policy = self._overdraft_policy
        if not policy.allows_expense(self._net_balance, amount):
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
            raise ValueError(
                f"Invalid transaction category: {transaction.category}")
        self._notify_observers(transaction)

    def undo_transaction(self, transaction):
        """
        Reverse a transaction that was applied earlier.

        The overdraft policy is skipped on purpose: undoing should always
        work. Observers are told about the reversal as the opposite
        transaction (e.g. undoing an expense looks like income).
        """
        if transaction.category == TransactionCategory.INCOME:
            self._net_balance -= transaction.amount
            opposite = TransactionCategory.EXPENSE
        elif transaction.category == TransactionCategory.EXPENSE:
            self._net_balance += transaction.amount
            opposite = TransactionCategory.INCOME
        else:
            raise ValueError(
                f"Invalid transaction category: {transaction.category}")
        self._notify_observers(Transaction(transaction.amount, opposite))

    def get_balance(self):
        """Get the current net balance."""
        return self._net_balance

    def summary(self):
        """Return a summary string of the net balance."""
        return f"Net balance: ${self._net_balance}"

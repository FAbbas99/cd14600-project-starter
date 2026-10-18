# transaction_adapter.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory

class TransactionAdapter:
    def __init__(self, external_transaction):
        self.external_transaction = external_transaction

    def to_transaction(self):
        """Convert an external transaction to a standard Transaction."""
        # Freelance income is always income. The invoice id and description
        # are specific to the external platform, so the app doesn't keep them.
        return Transaction(self.external_transaction.amount,
                           TransactionCategory.INCOME)

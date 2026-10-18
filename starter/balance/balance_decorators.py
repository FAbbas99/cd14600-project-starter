# balance_decorators.py
# Decorator pattern: wrap a balance to add validation or logging to
# apply_transaction without changing the Balance class itself.

import logging

from transaction.transaction_category import TransactionCategory

logger = logging.getLogger("finance")


class BalanceDecorator:
    """Base decorator. Forwards everything to the wrapped balance."""

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def apply_transaction(self, transaction):
        self._wrapped.apply_transaction(transaction)

    def __getattr__(self, name):
        # Only called for attributes not found here (get_balance, summary...)
        return getattr(self._wrapped, name)


class ValidatingBalanceDecorator(BalanceDecorator):
    """Rejects bad transactions before they reach the balance."""

    def apply_transaction(self, transaction):
        amount = transaction.amount
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Transaction amount must be a number.")
        if amount <= 0:
            raise ValueError("Transaction amount must be greater than zero.")
        if not isinstance(transaction.category, TransactionCategory):
            raise ValueError(
                "Transaction category must be a TransactionCategory.")
        super().apply_transaction(transaction)


class LoggingBalanceDecorator(BalanceDecorator):
    """Logs every transaction and whether it was accepted."""

    def apply_transaction(self, transaction):
        logger.info("Applying %s", transaction)
        try:
            super().apply_transaction(transaction)
        except ValueError as error:
            logger.warning("Rejected %s: %s", transaction, error)
            raise
        logger.info("Done. %s", self._wrapped.summary())

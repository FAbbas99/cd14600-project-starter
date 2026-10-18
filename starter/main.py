"""This module serves as the entry point for the program."""
import logging

from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver
from balance.balance_decorators import LoggingBalanceDecorator
from balance.balance_decorators import ValidatingBalanceDecorator
from balance.commands import ApplyTransactionCommand, CommandHistory
from budget.budget_strategy import BudgetPlanner
from budget.budget_strategy import FiftyThirtyTwentyStrategy
from budget.budget_strategy import ZeroBasedStrategy
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome


def main():
    logging.basicConfig(level=logging.INFO, format="  [log] %(message)s")

    print("Adding transactions...")

    balance = Balance.get_instance()
    balance.reset()
    balance.register_observer(PrintObserver())
    balance.register_observer(LowBalanceAlertObserver(threshold=100))

    # Decorators: validate first, then log whatever happens
    safe_balance = LoggingBalanceDecorator(ValidatingBalanceDecorator(balance))
    history = CommandHistory()

    # Create standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(1200, "INV-98765", "Mobile App Project")
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    # Each transaction goes through a command so it can be undone
    for transaction in all_transactions:
        history.execute(ApplyTransactionCommand(safe_balance, transaction))

    print(balance.summary())

    print("\nTrying an invalid transaction...")
    try:
        history.execute(ApplyTransactionCommand(
            safe_balance, Transaction(-20, TransactionCategory.EXPENSE)))
    except ValueError as error:
        print(f"Rejected: {error}")

    print("\nUndoing the last transaction...")
    history.undo()
    print(balance.summary())

    print("\nRedoing it...")
    history.redo()
    print(balance.summary())

    print("\nBudget plans for $1000 of income...")
    planner = BudgetPlanner(FiftyThirtyTwentyStrategy())
    print("50/30/20:", planner.plan(1000))
    planner.set_strategy(ZeroBasedStrategy({"Rent": 600, "Food": 250, "Fun": 150}))
    print("Zero-based:", planner.plan(1000))


if __name__ == "__main__":
    main()

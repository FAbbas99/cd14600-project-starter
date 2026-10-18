# Personal Finance Manager — Design Patterns Project

This project is a hands-on exercise in applying Object-Oriented Design Patterns to build a simplified personal finance manager.
You will implement and extend starter code to add functionality such as tracking transactions, adapting external data, observing balance changes, and ensuring proper architectural patterns.

## Getting Started

### Dependencies

Make sure you have python version >= 3.10.x installed on your computer. 


### Installation

1. Clone the repo:

```
bash
git clone https://github.com/udacity/cd14600-project-starter.git
cd cd14600-project-starter/starter
```

2. Run the Program: 
```
python main.py
```

## Testing

This project uses Python’s built-in unittest framework.

To run all tests:

```
python -m unittest discover
```

To run a single test file:
```
python -m unittest balance/test_balance_observer.py
```

### Break Down Tests

- test_balance.py → Verifies correct implementation of the Singleton Balance class.
- test_transaction.py → Confirms transactions update balances correctly.
- test_transaction_adapter.py → Ensures external income data is correctly adapted into Transaction objects.
- test_balance_observer.py → Validates that low-balance alerts are triggered at the correct threshold.

## Project Instructions

1. Implement Singleton Balance Class – Ensure only one balance object exists throughout the app.
2. Complete Transaction Class – Handle income and expense transactions.
3. Implement Adapter Pattern – Adapt external freelance income data into internal Transaction objects.
4. Implement Observer Pattern – Create a low balance observer that triggers an alert when funds drop too low.
5. Add Unit Tests – Write tests for all implemented functionality.
6. Choose and Implement a Fourth Pattern – Pick one additional design pattern (e.g., Strategy, Command, Decorator, etc.) and integrate it into your project.
7. Provide a Reflection – Add a short write-up in your repo (README or separate file) explaining your design choices.

## Design Patterns Used

| Pattern | Where | File |
|---|---|---|
| Singleton | One shared `Balance` for the whole app | `starter/balance/balance.py` |
| Adapter | Turns `ExternalFreelanceIncome` into a `Transaction` | `starter/transaction/transaction_adapter.py` |
| Observer | `PrintObserver` and `LowBalanceAlertObserver` listen to `Balance` | `starter/balance/balance_observer.py` |
| Strategy (my choice) | Swappable overdraft rules | `starter/balance/overdraft_policy.py` |
| Command (extra) | Undo/redo for transactions | `starter/balance/commands.py` |
| Strategy again (extra) | Budget planning (50/30/20, zero-based) | `starter/budget/budget_strategy.py` |
| Decorator (extra) | Validation and logging around the balance | `starter/balance/balance_decorators.py` |

## Reflection

### Why I picked Strategy
- For my extra pattern I wanted something that actually fit the balance code and didn't feel forced.
- The first question I asked myself was "should an expense be allowed if there isn't enough money?" and the answer depends on the user.
- I didn't want a bunch of if statements for that inside Balance, so I made an IOverdraftPolicy with three versions: AllowOverdraft, NoOverdraft and OverdraftLimit.
- Balance just asks whatever policy it has been given. The default allows overdrafts, so the starter tests (which expect -40) still pass.
- It helped testing the most because each rule is a tiny class I can test on its own.
- If I want a new rule later I write a new class and don't touch Balance.

### Singleton
- This was the one I understood best going in, but I still got stuck on some details.
- I used get_instance() and made __init__ raise an error if an instance already exists, so nobody can make a second Balance by accident.
- It made sense here because the app should only ever have one balance.
- The trade-off I ran into was testing. The instance lives for the whole test run, so one test could leak into the next.
- I fixed it by making reset() also clear the observers and the policy, and calling it in every setUp.
- Singletons feel a bit like global variables, so I would be careful using them for much else.

### Adapter
- TransactionAdapter takes the freelance income object and gives back a normal Transaction marked as income.
- The rest of the app never has to know about invoice IDs or project names.
- The trade-off is that I throw those details away, so that info is lost. To keep it I would have to add fields to Transaction.

### Observer
- Balance keeps a list of observers and calls update() on each one after a transaction is applied.
- This let me add the low balance alert and the printing without Balance knowing anything about either.
- One thing I had to figure out was that the alert needs to switch back off once the balance goes over the threshold, because the test checks for that.
- Another small trade-off is that add_income and add_expense don't notify anyone if I call them directly. Only apply_transaction does, because the observers need a transaction to report on.

### Command (undo/redo)
- After the four required patterns I wanted to try the extra ideas from the project suggestions, and undo seemed the most useful for a finance app.
- Each transaction gets wrapped in an ApplyTransactionCommand with execute() and undo(). A CommandHistory keeps two lists, one for undo and one for redo.
- The part that took me a while was that undo has to actually reverse the money. I added undo_transaction() to Balance, which subtracts an income or adds back an expense.
- I made undo skip the overdraft policy on purpose, because otherwise undoing something could get blocked, which would be confusing.
- Observers get told about an undo too. Since they expect a transaction, I send the opposite one (undoing an expense looks like income), so the print output says "Applied ... Income". It works but it's a bit of a shortcut.
- If a command fails (like a rejected expense) it doesn't get added to the history, so undo can't undo something that never happened.

### Strategy again (budget planning)
- This is a second use of Strategy, this time in a new budget folder, completely separate from the overdraft one.
- BudgetPlanner is given a strategy and calls allocate(income). I made 50/30/20 and zero-based.
- Zero-based needs the user's own amounts, so I pass them into the strategy when I create it. Anything left over shows up as "Unassigned", and it raises an error if the plan is more than the income.
- You can swap the strategy with set_strategy() while the app is running, which is the flexible part.
- Trade-off: the planner only shows a plan and doesn't connect to the Balance. I kept it simple, but it could be hooked up later.

### Decorator (validation and logging)
- I made a BalanceDecorator base class that wraps a balance and passes calls through, then two versions: one that validates and one that logs.
- ValidatingBalanceDecorator rejects amounts that are zero, negative, or not numbers (I also had to block True/False because Python counts them as numbers), and categories that aren't a TransactionCategory.
- LoggingBalanceDecorator uses Python's logging module and logs each transaction and whether it was accepted or rejected.
- They stack, so in main.py I wrapped logging around validating around the real balance. The order matters, because logging on the outside can log the rejection.
- I didn't put the validation inside Balance itself, since the starter tests expect Balance to behave a certain way (like raising ValueError for a fake category). The decorator lets me add checks without changing it.
- Trade-off: I used __getattr__ to forward other methods like get_balance(), which is handy but a bit magical and harder to follow when I first read it.

### Overall
- The biggest thing I learned is that these patterns make it easier to change one piece without breaking the others.
- The downside is more files and classes than a quick script would need, which felt like a lot for such a small app. By the end I had seven pattern uses in a program that would fit in one file.
- Passing in the observers, the policies and the wrapped balance from outside (in main.py and the tests) made testing a lot simpler.
- The patterns also worked well together. For example a command can wrap a decorated balance and not care that it is decorated.

## Running

```
cd starter
python main.py
python -m unittest discover
```

## Built With

* [Python](https://www.python.org/) – Main programming language
* [unittest](https://docs.python.org/3/library/unittest.html) – Testing framework
* [PEP8](https://peps.python.org/pep-0008/) – Style guide for Python code

## License

[License](LICENSE.txt)

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

I just finished learning design patterns, so this project was my first time
using them in a real program. Here is what I used and what I learned.

### The four required patterns

#### Singleton (Balance)
- Why I chose it: the app should only ever have one balance. If two parts of the code each had their own Balance they would show different amounts.
- What I did: I control object creation in __new__, which makes the one instance the first time and returns that same object every time after. get_instance() just calls Balance(), so there is only one way objects get created.
- Because Python runs __init__ on every Balance() call, I added an _initialized flag so the state is only set up once. Otherwise a second Balance() would wipe out the balance.
- My first version put the check in __init__ instead, and my project feedback caught that it did not work. Calling Balance() before the first get_instance() made a separate balance that was never saved. My test missed it because setUp() already called get_instance(), so I added a test that clears the instance first.
- How it helped: every part of the app (main.py, the commands, the tests) sees the same balance.
- Trade-off: the __new__ plus _initialized combo is a little harder to understand than a plain class. Also, the instance stays alive for the whole test run, so one test could change the balance for the next one. I fixed it by having reset() clear the balance, observers and policy, and calling it in every setUp.
- Another thing I noticed: a Singleton is basically a global variable, so I would not want to use it for lots of things.

#### Adapter (TransactionAdapter)
- Why I chose it: the freelance platform gives me an ExternalFreelanceIncome with an invoice ID and project name, but my app only understands Transaction.
- What I did: to_transaction() reads the amount and builds a normal INCOME Transaction.
- How it helped: the rest of the app never has to know about invoices or the other platform.
- Trade-off: I throw the invoice ID and project name away, so that info is lost. To keep it I would have to add fields to Transaction.

#### Observer (PrintObserver and LowBalanceAlertObserver)
- Why I chose it: I wanted alerts and printing without Balance knowing how either works.
- What I did: Balance keeps a list of observers and calls update() on each one after a transaction is applied. PrintObserver prints the new balance. LowBalanceAlertObserver sets alert_triggered and prints an alert when the balance is under the threshold.
- How it helped: I can add or remove observers without touching Balance.
- Challenge: the alert has to switch back off once the balance goes back over the threshold. I only figured that out by reading the test.
- Trade-off: add_income() and add_expense() do not notify anyone if I call them directly, only apply_transaction() does, because observers need a transaction to report on.

#### Strategy (my choice, overdraft rules)
- Why I chose it: "should an expense be allowed when there isn't enough money?" has more than one right answer, and I did not want a pile of if statements inside Balance.
- Where it fits: Balance holds an overdraft policy and asks it before subtracting an expense. There are three policies in overdraft_policy.py: AllowOverdraft (the default), NoOverdraft and OverdraftLimit.
- How it improves flexibility: I can swap the rule with set_overdraft_policy() while the app is running.
- How it improves testability: each rule is a tiny class that I can test by itself.
- How it improves scalability: a new rule is a new class and Balance does not change.
- Trade-off: three small classes for something an if statement could do. It was only worth it because there are several rules.

### Extra patterns I added
- Command (undo/redo):
  - Each transaction is wrapped in an ApplyTransactionCommand, and a CommandHistory keeps an undo list and a redo list.
  - I had to add undo_transaction() to Balance so undo really reverses the money. It skips the overdraft policy on purpose so an undo never gets blocked.
  - Shortcut: observers get the opposite transaction on undo, so the output says "Applied ... Income" when I undo an expense.
- Strategy again (budget planning):
  - BudgetPlanner uses a swappable strategy: 50/30/20 or zero-based.
  - It only makes a plan and does not connect to the Balance yet. I kept it simple.
- Decorator (validation and logging):
  - A validating decorator rejects bad amounts and categories, and a logging decorator logs every transaction. They stack, so main.py wraps logging around validating around the real balance.
  - I put the checks in a decorator and not inside Balance so the starter tests for Balance would still work.
  - I used __getattr__ to pass other calls through, which is handy but a bit confusing to read.

### Overall
- The main thing I learned is that patterns make it easier to change one part without breaking another.
- Trade-off: the project has a lot more files and classes than a quick script would. For an app this small it felt like too much sometimes.
- Dependency injection: I pass the observers, the policies and the wrapped balance in from outside (in main.py and the tests), which made testing much easier. But Balance itself is still reached through get_instance(), so that part is not fully injected. That is the cost of using a Singleton.

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

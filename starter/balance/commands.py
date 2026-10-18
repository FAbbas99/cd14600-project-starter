# commands.py
# Command pattern: each action on the balance is an object that can be
# executed and undone, so a history can step backwards and forwards.


class ICommand:
    def execute(self):
        raise NotImplementedError("Subclasses must implement execute.")

    def undo(self):
        raise NotImplementedError("Subclasses must implement undo.")


class ApplyTransactionCommand(ICommand):
    """Applies a transaction to a balance (or a decorated balance)."""

    def __init__(self, balance, transaction):
        self.balance = balance
        self.transaction = transaction

    def execute(self):
        self.balance.apply_transaction(self.transaction)

    def undo(self):
        self.balance.undo_transaction(self.transaction)


class CommandHistory:
    """Runs commands and remembers them for undo/redo."""

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def execute(self, command):
        # If execute raises (e.g. rejected by a policy) nothing is recorded.
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self):
        """Undo the last command. Returns False if there is nothing to undo."""
        if not self._undo_stack:
            return False
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return True

    def redo(self):
        """Redo the last undone command. Returns False if there is none."""
        if not self._redo_stack:
            return False
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return True

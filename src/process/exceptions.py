class MaxChildrenExceededError(Exception):
    """Exception raised when attempting to create more child agents than allowed."""
    def __init__(self, max_children: int):
        self.max_children = max_children
        self.message = f"Cannot create new child agent: Maximum number of children ({max_children}) already reached"
        super().__init__(self.message)

class ChildAgentNotFoundError(Exception):
    """Exception raised when trying to interact with a non-existent child agent."""
    def __init__(self, name: str):
        self.name = name
        self.message = f"Child agent '{name}' not found"
        super().__init__(self.message)

class ChildAgentExistsError(Exception):
    """Exception raised when trying to create a child agent with a name that already exists."""
    def __init__(self, name: str):
        self.name = name
        self.message = f"Child agent '{name}' already exists"
        super().__init__(self.message)

class ChildAgentNotRunningError(Exception):
    """Exception raised when trying to interact with a child agent that is not running."""
    def __init__(self, name: str):
        self.name = name
        self.message = f"Child agent '{name}' is not running"
        super().__init__(self.message)

class ChildAgentTimeoutError(Exception):
    """Exception raised when a request to a child agent times out."""
    def __init__(self, name: str):
        self.name = name
        self.message = f"Timeout waiting for response from child agent '{name}'"
        super().__init__(self.message)

class ChildAgentOperationError(Exception):
    """Exception raised when an operation on a child agent fails."""
    def __init__(self, name: str, operation: str, error: str):
        self.name = name
        self.operation = operation
        self.error = error
        self.message = f"Error during {operation} on child agent '{name}': {error}"
        super().__init__(self.message)

class MaxChildrenExceededError(Exception):
    """Exception raised when maximum number of child agents is reached."""

    def __init__(self, max_children: int):
        self.max_children = max_children
        self.message = (
            f"Cannot create new child agent: Maximum number of "
            f"children ({max_children}) already reached"
        )
        super().__init__(self.message)


class ChildAgentNotFoundError(Exception):
    """Exception raised when referencing a nonexistent child agent."""

    def __init__(self, name: str):
        self.name = name
        self.message = f"Child agent '{name}' does not exist"
        super().__init__(self.message)


class ChildAgentExistsError(Exception):
    """Exception raised when creating a child agent with a duplicate name."""

    def __init__(self, name: str):
        self.name = name
        self.message = f"Child agent '{name}' already exists"
        super().__init__(self.message)


class ChildAgentNotRunningError(Exception):
    """Exception raised when accessing a stopped child agent."""

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


class UnknownToolError(Exception):
    """Exception raised when trying to use a tool that is not in the tool mapping."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.message = (
            f"Unknown tool: '{tool_name}' not found in any registered MCP servers"
        )
        super().__init__(self.message)

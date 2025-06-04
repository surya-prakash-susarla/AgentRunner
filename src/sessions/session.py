from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Session:
    """A container for managing conversation session data.

    Stores the base instruction, message history, and interaction timing for a
    conversation session between a user and the system.
    """

    base_instruction: str
    user_messages: List[str]
    system_messages: List[str]
    last_interaction_time: datetime
    current_turn: str  # Indicates whose turn it is: 'user' or 'system'

    def __str__(self) -> str:
        """Return a string representation of the session.

        Returns:
            A formatted string showing the base instruction and message history.

        """
        conversation = []
        conversation.append(f"Base Instruction: {self.base_instruction}\n")
        conversation.append(f"Current Turn: {self.current_turn}")
        conversation.append(f"Last Interaction: {self.last_interaction_time}\n")
        conversation.append("Conversation History:")

        for i, (user, system) in enumerate(
            zip(self.user_messages, self.system_messages), 1
        ):
            conversation.append(f"\nTurn {i}:")
            conversation.append(f"User: {user}")
            conversation.append(f"System: {system}")

        # Add any remaining messages if the lists have different lengths
        remaining_user = self.user_messages[len(self.system_messages) :]
        for msg in remaining_user:
            conversation.append(f"\nUser: {msg}")
            conversation.append("System: <awaiting response>")

        return "\n".join(conversation)

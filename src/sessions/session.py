from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Session:
    base_instruction: str
    user_messages: List[str]
    system_messages: List[str]
    current_turn: str
    last_interaction_time: datetime

    def __str__(self) -> str:
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

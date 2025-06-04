import uuid
from datetime import datetime
from typing import Dict

from src.sessions.session import Session


class SessionsManager:
    """Manager for handling chat sessions and their associated state."""

    def __init__(self) -> None:
        # Initialize dict to hold session id to session object mapping
        self.sessions: Dict[str, Session] = {}

    def create_session(self, base_instruction: str) -> str:
        """Create a new UUID for the session and initialize a session object to store the instruction.

        Args:
            base_instruction: The base instruction to initialize the session with.

        Returns:
            str: The newly created session ID.
        """
        session_id: str = str(uuid.uuid4())
        self.sessions[session_id] = Session(
            base_instruction=base_instruction,
            user_messages=[],
            system_messages=[],
            current_turn="user",
            last_interaction_time=datetime.now(),
        )
        return session_id

    def get_session_details(self, session_id: str) -> Session | None:
        """Get the session details for a session object.

        Args:
            session_id: The ID of the session to retrieve.

        Returns:
            Session | None: The session object if found, None otherwise.
        """
        if session_id in self.sessions:
            return self.sessions[session_id]
        return None

    def record_user_interaction(self, session_id: str, user_message: str) -> None:
        """Update the given session with the user message and set turn to system.

        Args:
            session_id: The ID of the session to update.
            user_message: The message from the user to record.
        """
        if session_id in self.sessions:
            self.sessions[session_id].user_messages.append(user_message)
            self.sessions[session_id].current_turn = "system"
            self.sessions[session_id].last_interaction_time = datetime.now()
        else:
            print(f"Session {session_id} not found")

    def record_system_interaction(self, session_id: str, system_message: str) -> None:
        """Update the given session with the system message and set turn to user.

        Args:
            session_id: The ID of the session to update.
            system_message: The message from the system to record.
        """
        if session_id in self.sessions:
            self.sessions[session_id].system_messages.append(system_message)
            self.sessions[session_id].current_turn = "user"
            self.sessions[session_id].last_interaction_time = datetime.now()
        else:
            print(f"Session {session_id} not found")

    def delete_session(self, session_id: str) -> None:
        """Remove a session.

        Args:
            session_id: The ID of the session to delete.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        else:
            print(f"Session {session_id} not found")

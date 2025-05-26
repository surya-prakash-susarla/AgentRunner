

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class Session:
  base_instruction: str
  user_messages: List[str]
  system_messages: List[str]
  current_turn: str
  last_interaction_time: datetime

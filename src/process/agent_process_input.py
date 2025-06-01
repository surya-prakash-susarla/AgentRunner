from dataclasses import dataclass
from src.config.config_manager import RunnerType


@dataclass
class AgentProcessInput:
    name: str
    instruction: str
    child_type: RunnerType
    tool_names: str

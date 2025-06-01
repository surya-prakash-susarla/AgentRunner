import os
from typing import Optional
from src.runner.gemini_runner import GeminiRunner
from src.runner.agent_runner import AgentRunner
from src.config.config_manager import RunnerType, get_config_manager


def create_runner(type: RunnerType, instruction: str) -> Optional[AgentRunner]:
    """Create an appropriate runner instance and set up its runtime environment.

    Args:
        type: Type of the runner to create (e.g. GEMINI)
        instruction: Initial instruction/system prompt for the runner

    Returns:
        An instance of AgentRunner or None if creation fails
    """
    # Set up runtime environment first
    runtime = get_config_manager().agents[type]
    
    if type == RunnerType.GEMINI:
        os.environ["GOOGLE_API_KEY"] = runtime.api_key
        return GeminiRunner(instruction=instruction)
    else:
        return None

from typing import Optional
from src.runner.agent_runner import AgentRunner
from src.config.config_manager import RunnerType

def generate_runner(type: RunnerType, instruction: str) -> Optional[AgentRunner]:
    """Generate an appropriate runner instance based on configuration.
    
    Args:
        name: Name of the agent/runner to generate
        instruction: Initial instruction/system prompt for the runner
        
    Returns:
        An instance of AgentRunner or None if generation fails
    """
    if type == RunnerType.GEMINI:
        from src.runner.gemini_runner import GeminiRunner
        return GeminiRunner(instruction=instruction)
    else:
        return None

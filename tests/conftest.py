"""Shared pytest fixtures."""

import pytest

from src.process.agent_process_input import AgentProcessInput


@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing."""
    return {
        "agents": {
            "gemini": {"api_key": "test-key", "is_main": True, "model": "gemini-pro"}
        },
        "logging": {"level": "INFO"},
        "mcp": {"port": 5000, "host": "localhost"},
    }


@pytest.fixture
def sample_agent_input():
    """Provide a sample AgentProcessInput for testing."""
    return AgentProcessInput(
        name="test-agent",
        instruction="Test instruction",
        child_type="gemini",
        tool_names=["tool1", "tool2"],
    )

"""Test agent process input validation."""

import pytest

from src.process.agent_process_input import AgentProcessInput
from src.process.exceptions import ValidationError


def test_agent_process_input_validation(sample_agent_input):
    """Test that AgentProcessInput properly validates its fields."""
    # Test valid input
    assert sample_agent_input.name == "test-agent"
    assert sample_agent_input.child_type == "gemini"
    assert len(sample_agent_input.tool_names) == 2

    # Test invalid name
    with pytest.raises(ValidationError):
        AgentProcessInput(
            name="",  # Empty name should fail
            instruction="Test instruction",
            child_type="gemini",
            tool_names=["tool1"],
        )

    # Test invalid child_type
    with pytest.raises(ValidationError):
        AgentProcessInput(
            name="test-agent",
            instruction="Test instruction",
            child_type="invalid-type",  # Invalid type should fail
            tool_names=["tool1"],
        )

    # Test invalid tool_names
    with pytest.raises(ValidationError):
        AgentProcessInput(
            name="test-agent",
            instruction="Test instruction",
            child_type="gemini",
            tool_names=[],  # Empty tool list should fail
        )

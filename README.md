# Replica LLM CLI

A CLI tool for running and managing LLM agents.

## Configuration

The configuration file is stored at `~/.replica-llm/config.json`. Here's an example configuration:

```json
{
  "agents": {
    "main": {
      "runtime": {
        "runner": "gemini",
        "isMain": true,
        "api_key": "your-api-key-here",
        "model": "gemini-pro"
      },
      "tools": [
        "echo_tools",
        "replicator_tools"
      ]
    },
    "assistant": {
      "runtime": {
        "runner": "gemini",
        "isMain": false,
        "api_key": "your-api-key-here",
        "model": "gemini-pro"
      },
      "tools": ["echo_tools"]
    }
  },
  "runtime": {
    "maxGlobalChildren": 100,
    "defaultTimeoutSeconds": 60
  },
  "toolServers": {}
}
```

### Configuration Structure

#### Agents
Each agent in the system has its own configuration under the `agents` object:

- `runtime`: Core configuration for the agent
  - `runner`: Type of runner to use (must be "gemini")
  - `isMain`: Whether this is the main agent (only one agent should be marked as main)
  - `api_key`: API key for the model service (optional)
  - `model`: Model to use (defaults to "gemini-pro")
- `tools`: List of tool servers this agent has access to

#### Runtime
Global runtime settings:

- `maxGlobalChildren`: Maximum number of child processes allowed globally
- `defaultTimeoutSeconds`: Default timeout for operations

#### Tool Servers
Configuration for tool servers (structure to be expanded based on needs)

## Usage

```bash
# Start an interactive chat session
replica-llm chat

# Edit configuration
replica-llm config
```

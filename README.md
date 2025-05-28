# Replica LLM CLI

A CLI tool for running and managing LLM agents.

## TODO

### Immediate Implementation Tasks
1. **Runner Type System**
   - Create a tool to expose runner names to agents
   - Ensure names are used exactly as exposed in agent interactions
   - Add validation against these exposed names

2. **Root Runner Generation**
   - Implement `generate_root_runner` in runner_generator.py
   - Add support for main agent detection and delegation capabilities
   - Include custom instruction set for child agent management

3. **Main CLI Integration**
   - Replace direct GeminiRunner creation with generate_root_runner
   - Update chat command to use root runner
   - Ensure proper cleanup and resource management

4. **Child Agent Creation Flow**
   - Update replicator tools to validate runner types
   - Integrate with exposed runner names system
   - Implement proper parent-child relationship management

### Long-Term Enhancements

1. **MCP Tool Integration**
   - Add MCP tool configuration to JSON schema
   - Implement external MCP tool loading
   - Add validation for tool configurations
   - Consider tool versioning and compatibility

2. **API Key Management**
   - Implement secure API key storage
   - Add key rotation capabilities
   - Consider environment variable integration
   - Add validation for required keys

3. **Recursive Agent Creation**
   - Add `is_recursible` flag to agent configuration
   - Implement recursion depth limits
   - Add safeguards against infinite recursion
   - Implement proper resource cleanup for recursive chains

### Additional Considerations
1. Error handling for runner type mismatches
2. Proper cleanup of child agent resources
3. Validation of parent-child relationships
4. Monitoring and logging for agent hierarchies
5. Configuration versioning and migration support

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

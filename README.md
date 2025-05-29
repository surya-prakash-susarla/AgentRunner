# Replica LLM CLI

A CLI tool for running and managing LLM agents.

## TODO

### Immediate Implementation Tasks
1. **Runner Type System** [src/tools/replicator_tools.py]
   - Create a tool to expose runner names to agents (`get_available_runners()`)
   - Ensure names are used exactly as exposed in agent interactions
   - Add validation against these exposed names
   - Reference RunnerType enum from config_manager.py

2. **Root Runner Generation** [src/runner/runner_generator.py]
   - Implement `generate_root_runner()` method
   - Add support for main agent detection and delegation capabilities
   - Include custom instruction set for child agent management
   - Use ConfigManager to validate runner types

3. **Main CLI Integration** [src/main.py]
   - Replace direct GeminiRunner creation with `runner_generator.generate_root_runner()`
   - Update chat command to use root runner
   - Ensure proper cleanup and resource management via cleanup_manager
   - Add error handling for missing or invalid main agent

4. **Child Agent Creation Flow** [src/tools/replicator_tools.py]
   - Update replicator tools to validate runner types using `get_available_runners()`
   - Integrate with exposed runner names system
   - Implement proper parent-child relationship management
   - Use runner_generator for child agent creation

### Long-Term Enhancements

1. **MCP Tool Integration** [src/config/config_manager.py, src/tools/**]
   - Add MCP tool configuration to JSON schema in ToolServerConfig
   - Implement external MCP tool loading mechanism
   - Add validation for tool configurations
   - Consider tool versioning and compatibility
   - Update ConfigManager to handle tool server configs

2. **API Key Management** [src/config/config_manager.py, src/runner/agent_runner.py]
   - Implement secure API key storage
   - Add key rotation capabilities
   - Consider environment variable integration
   - Add validation for required keys
   - Update AgentRunner to properly utilize API keys

3. **Recursive Agent Creation** [src/config/config_manager.py, src/process/replica_manager.py]
   - Add `is_recursible` flag to AgentRuntime class
   - Implement recursion depth limits in ReplicaManager
   - Add safeguards against infinite recursion
   - Implement proper resource cleanup for recursive chains
   - Update process management to track recursion depth

### Additional Considerations
1. Error handling for runner type mismatches [src/runner/runner_generator.py]
2. Proper cleanup of child agent resources [src/utils/cleanup.py]
3. Validation of parent-child relationships [src/process/replica_manager.py]
4. Monitoring and logging for agent hierarchies [src/utils/logging_config.py]
5. Configuration versioning and migration support [src/config/config_handler.py]

## Configuration

The configuration file is stored at `~/.replica-llm/config.json`. Here's an example configuration:

```json
{
  "runners": [
      {
        "type": "gemini",
        "isMain": true,
        "apiKey": "your-api-key-here",
        "model": "gemini-pro",
        "tools": ["tool1", "tool2", "tool3"]
      },
      {
        "type": "chatgpt",
        "apiKey": "your-api-key-here",
        "model": "gpt-4o",
        "tools": ["tool1", "tool2", "tool3"]
      }
  ],
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

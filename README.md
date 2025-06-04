# Replica LLM CLI

A sophisticated multi-agent orchestration system that allows dynamic creation and management of specialized LLM agents.

## Features

- 🤖 Dynamic Agent Creation - Spawn specialized agents for different tasks
- 🔄 Tool Distribution - Smart distribution of capabilities across agents
- 🎯 Task Delegation - Efficient routing of tasks to appropriate agents
- 🔒 Security-First Design - Controlled access to system tools
- 🖥️ Beautiful TUI (Coming Soon) - Rich terminal interface for agent management

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- make (optional, for development commands)

## Quick Start

1. Clone the repository:
```bash
git clone <your-repo-url>
cd replica_llm/cli
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install the package:
```bash
pip install -e ".[dev]"  # Install with development dependencies
# OR
make install  # If you have make installed
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Run the CLI:
```bash
replica-llm chat  # Start a chat session
```

## Development

This project uses modern Python tools for quality and consistency:

- 📝 **Code Formatting**: black, isort
- 🔍 **Linting**: ruff, mypy
- 🧪 **Testing**: pytest

### Development Commands

With Make:
```bash
make setup      # Full setup: clean, install, format, lint, test
make format     # Format code with black and isort
make lint       # Run all linters
make test       # Run tests with coverage
make clean      # Clean build artifacts
```

Without Make:
```bash
pip install -e ".[dev]"
black src tests
isort src tests
mypy src
ruff check src tests
pytest
```

## Project Structure

```
replica_llm/cli/
├── src/                    # Source code
│   ├── config/            # Configuration management
│   ├── process/           # Agent process handling
│   ├── runner/            # Agent runners and orchestration
│   ├── sessions/          # Chat session management
│   ├── tools/             # Tool definitions and MCP integration
│   └── utils/             # Utilities and helpers
├── tests/                 # Test suite
├── setup.py               # Package setup
└── pyproject.toml         # Project configuration
```

## Configuration

The system can be configured through:
1. Environment variables (see `.env.example`)
2. Configuration files in the config directory
3. Command-line arguments

### Environment Variables

Required:
- `GOOGLE_API_KEY`: Your Google API key for Gemini
- `MCP_PORT`: Port for Model Context Protocol server

Optional:
- `LOG_LEVEL`: Logging level (default: INFO)
- `CONFIG_PATH`: Custom config file path

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`make test`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

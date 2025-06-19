# Log Analysis System

A simple log analysis tool.

## Overview

This system helps with intelligent log analysis by:
- Finding and extracting relevant logs
- Analyzing patterns and anomalies
- Recommending solutions based on identified issues
- Using AI (via Ollama) to enhance solution recommendations

## Architecture

The system uses the following components:

### Core Components
- **Log Finder**: Searches and finds log files matching specific criteria
- **Log Parser**: Extracts structured data from log files
- **Pattern Analyzer**: Identifies trends and patterns in logs
- **Solution Recommender**: Suggests fixes based on identified issues
- **AI Enhancement**: Uses Ollama with local LLM models to provide improved solutions and recommendations

## Installation

### Requirements
- Python 3.10+
- Ollama (for AI enhancement)

For Mac:
```bash
brew install python
brew install ollama
```

### Setup

1. Clone the repository and run the setup script:
```bash
git clone https://github.com/yourusername/log-analysis-system.git
cd log-analysis-system
chmod +x setup.sh
./setup.sh
```

2. The setup script will:
   - Check for Ollama installation and required models
   - Create a virtual environment
   - Install dependencies
   - Set up the directory structure
   - Generate sample log files

### AI Enhancement Setup

To enable AI enhancement for better solution recommendations:

1. Install Ollama from [ollama.com](https://ollama.com)

2. Pull the required models:
```bash
ollama pull llama3.2
ollama pull llama3.1
ollama pull deepseek-r1
```

3. Start the Ollama server:
```bash
ollama serve
```

## Usage

### Log Analysis

For a comprehensive log analysis:
```bash
./run_analysis.sh --logs data/logs --term error
```

#### Command-line Options

The command-line tool supports the following options:

- `--logs PATH`: Directory containing log files
- `--term STRING`: Search term to look for in logs
- `--output FILE`: Write results to a JSON file
- `--verbose`: Enable detailed output
- `--disable-ai`: Disable AI enhancement
- `--model MODEL_NAME`: Specify which Ollama model to use
- `--debug`: Enable debug mode with additional information

Examples:

```bash
# Analyze logs with a specific model
./run_analysis.sh --model deepseek-r1 --logs data/logs --term error

# Save results to a file
./run_analysis.sh --logs data/logs --term error --output results.json

# Enable verbose and debug output
./run_analysis.sh --logs data/logs --term error --verbose --debug
```

You can also set the model via environment variable:
```bash
OLLAMA_MODEL=deepseek-r1 ./run_analysis.sh --logs data/logs --term error
```

### Web Interface

To launch the Streamlit web UI:
```bash
./run_ui.sh
```

#### UI Command-line Options

The UI tool supports the following options:

- `--verbose`: Enable detailed output
- `--disable-ai`: Disable AI enhancement
- `--api-base URL`: Specify the Ollama API base URL (default: http://localhost:11434)
- `--debug`: Enable debug mode with additional information in the UI

Examples:

```bash
# Run UI with a specific Ollama API endpoint
./run_ui.sh --api-base http://192.168.1.100:11434

# Enable debug mode
./run_ui.sh --debug
```

#### Debug Mode

Debug mode can be enabled in three ways:

1. Command-line flag: `--debug`
2. Environment variable: `DEBUG=1`
3. URL parameter: `?debug=1` (UI only)

In debug mode, you get:
- Additional information in the console logs
- A debug panel in the UI showing environment variables and Ollama connection status
- More detailed error messages

#### Web UI Features

In the web UI, you can:
- Configure log source directories
- Set search terms
- Enable/disable AI enhancement
- Select which Ollama model to use
- View enhanced solution recommendations
- See error patterns and log matches
- Access debug information if debug mode is enabled

### Demo Mode

To run a demonstration with automatically generated logs:
```bash
./run_demo.sh
```

You can specify which model to use in demo mode:
```bash
./run_demo.sh --model deepseek-r1
```

## AI Enhancement Features

When AI enhancement is enabled:

- Solutions will be more detailed and customized to your specific log patterns
- You'll see additional contextual information and explanation for each solution
- Both the UI and command-line output will clearly indicate when AI is being used
- Each enhanced solution will be marked with "✨ AI Enhanced with Ollama"

### AI Enhancement Status

You can tell if AI enhancement is active by:
1. The status banner at the top of the UI showing which Ollama model is in use
2. The "✨ AI Enhanced with Ollama" indicator on solutions
3. The terminal output showing "AI ENHANCEMENT IS ENABLED"

### Ollama Configuration

The system supports connecting to Ollama in several ways:

1. Default local connection (http://localhost:11434)
2. Custom API endpoint via environment variable: `OLLAMA_API_BASE=http://your-server:11434`
3. Command-line parameter for the UI: `--api-base http://your-server:11434`

### Configuring Ollama Models

The system supports any model available in your Ollama installation. To use a different model:

1. Pull the model using Ollama: `ollama pull model-name`
2. Select the model in the UI dropdown menu, or
3. Set the `OLLAMA_MODEL` environment variable when running from command line:
   ```bash
   OLLAMA_MODEL=llama3.2 ./run_analysis.sh
   ```
4. Use the `--model` command line parameter:
   ```bash
   ./run_analysis.sh --model deepseek-r1
   ```

### Available Models

The system is configured to work with these models out of the box:
- `llama3.2`: Fast, efficient model for general analysis
- `llama3.1`: Larger model with more comprehensive responses
- `deepseek-r1`: Specialized model with strong technical capabilities

You can compare performance across models to determine which works best for your specific log analysis needs.

## Environment Variables

The system uses the following environment variables:

- `OLLAMA_API_BASE`: Base URL for the Ollama API server (default: http://localhost:11434)
- `OLLAMA_MODEL`: Default Ollama model to use (default: llama3.2)
- `DISABLE_AI_ENHANCEMENT`: Set to "true" to disable AI enhancement
- `DEBUG`: Set to "1" to enable debug mode

These can be set in your environment or in a `.env` file in the project root.

## Extending the System

### Adding New Log Sources

1. Update the log parsing functions in `analyze_logs.py` to support new log formats
2. Add new regex patterns to extract data from different log formats

### Adding New Solution Patterns

1. Enhance the `suggest_solutions` function in `analyze_logs.py`
2. Add new pattern matching logic for different types of issues

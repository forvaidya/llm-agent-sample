# Weather Agent

This repository contains a Python-based weather agent that fetches weather data for a specific location (hardcoded to Bangalore) and posts the results to Slack. The project is designed to demonstrate the basics of building an agent in Python, with a focus on asynchronous workflows, API integration, and logging.

## Features
- Fetches weather data from the OpenWeatherMap API.
- Posts weather updates to a Slack channel.
- Asynchronous design for efficient API calls.
- Configurable logging levels, including an option to disable logging entirely.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- A Slack workspace and a bot token with permissions to post messages.
- An OpenWeatherMap API key.

### Installation
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd openrouter-examples/src
   ```

2. Create a `.env` file in the parent directory (`../`) with the following keys:
   ```
   OPENWEATHER_API_KEY=<your_openweathermap_api_key>
   SLACK_BOT_TOKEN=<your_slack_bot_token>
   OPENROUTER_API_KEY=<your_openrouter_api_key>  # Add your OpenRouter API key here
   LOG_LEVEL=DEBUG  # Optional: Set to NONE to disable logging
   ```
   Replace `<your_openweathermap_api_key>` and `<your_slack_bot_token>` with your actual API keys.

3. Install the required Python packages:
   ```bash
   pip install -r ../requirements.txt
   ```

### Running the Agent
Start the agent by running the following command:
```bash
python api_server.py
```

You can then interact with the agent by sending HTTP POST requests to its endpoint.

### Example Request
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "what is bangalore weather looking like"}' http://127.0.0.1:8000/ask
```

## Notes
- Ensure the `.env` file is created in the parent directory (`../`) with real values before running the agent.
- Most of the coding for this project was done using GitHub Copilot, which assisted in generating and refining the code.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

Happy coding!

# AI Slack Bot

A conversational Slack bot powered by [`pydantic.ai`](https://ai.pydantic.dev) that answers questions and remembers channel-specific context.

## Features

-   **Conversational AI:** Responds to user questions and commands when mentioned in a channel.
-   **Channel-Specific Memory:** Maintains a separate conversation history for each channel, allowing for contextual follow-up questions.
-   **Threaded Conversations:** Acknowledges requests and replies within threads to keep channels clean.
-   **Easy to Run:** Simple setup and execution using shell scripts.

## Prerequisites

-   Python 3.9+
-   A Slack Workspace with permissions to create and install apps.
-   Gemini, OpenAI or other LLM api token

## Setup and Installation

Follow these steps to set up and run the bot. This guide assumes a Debian-based Linux environment (like Ubuntu). Tested on Ubuntu 24.04

### 1. Clone the Repository

```bash
git clone https://github.com/joerawr/ai-slack-bot.git
cd ai-slack-bot
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using pip.

```bash
pip install --upgrade pip
pip install pydantic-ai slack-bolt boto3 uv psutil
```

## Configuration

### 1. Set Up Your Slack App

`TODO: reconfirm Slack app setup, with screen captures`

You need to create a Slack App in your workspace to get the required tokens.

1.  Go to [https://api.slack.com/apps](https://api.slack.com/apps) and click "Create New App".
2.  Choose "From an app manifest" and select your workspace.
3.  Copy the contents of the `manifest.yml` file from this repository and paste it into the manifest editor on the Slack website.
4.  Create the app.
5.  Navigate to the **"Install App"** page in the sidebar and install the app to your workspace.
6.  Go to **"OAuth & Permissions"** and copy the **Bot User OAuth Token** (it starts with `xoxb-`).
7.  Go to **"Basic Information"**, scroll down to "App-Level Tokens", and generate a new token with the `connections:write` scope. Copy this token (it starts with `xapp-`).

### 2. Export Environment Variables

The bot requires three Slack environment variables to be set and an API key for the desired LLM. It's best practice to add these to your shell's configuration file (e.g., `~/.bashrc` or `~/.zshrc`) and then restart your shell.  

```bash
#Slack Tokens
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_APP_TOKEN="xapp-your-token-here"
export SLACK_TEAM_ID="T12345678"

#LLM API KEY
export GEMINI_API_KEY="your-api-key-here"
-or-
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

Once the setup and configuration are complete, you can start the bot using the provided script. This will start the bot and automatically restart it if it crashes.

```bash
./restart_slack_bot.sh
```

To stop the bot, use:

```bash
./stop_slack_bot.sh
```

## Project Structure

-   `slack_bot.py`: The main entry point that starts the Slack listener.
-   `slack_message_handler.py`: Handles incoming Slack mentions, processes the request, and sends the response.
-   `slack_agent.py`: Contains the core LLM agent logic, using `pydantic.ai` to interact with the language model.
-   `logger_config.py`: Configures logging for the application.
-   `history/`: Directory where conversation history is stored as JSON files, one per channel.
-   `logs/`: Directory where log files are written.
-   `restart_slack_bot.sh` / `stop_slack_bot.sh`: Scripts to manage the bot process.
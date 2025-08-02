# AI Slack Bot (Docker Edition)

A conversational Slack bot powered by [`pydantic.ai`](https://ai.pydantic.dev) that answers questions and remembers channel-specific context. This project is designed to be run as a Docker container.

## Features

-   **Conversational AI:** Responds to user questions and commands when mentioned in a channel.
-   **Channel-Specific Memory:** Maintains a separate conversation history for each channel, allowing for contextual follow-up questions.
-   **Threaded Conversations:** Acknowledges requests and replies within threads to keep channels clean.
-   **Containerized:** Runs in a Docker container for easy and consistent deployment.

## Prerequisites

-   Docker installed and running on your system.
-   A Slack Workspace with permissions to create and install apps.
-   A Gemini, OpenAI, or other LLM API key.

## Configuration

### 1. Set Up Your Slack App

You need to create a Slack App in your workspace to get the required tokens.

1.  Go to [https://api.slack.com/apps](https://api.slack.com/apps) and click "Create New App".
2.  Choose "From an app manifest" and select your workspace.
3.  Copy the contents of the `manifest.yml` file from this repository and paste it into the manifest editor on the Slack website.
4.  Create the app.
5.  Navigate to the **"Install App"** page in the sidebar and install the app to your workspace.
6.  Go to **"OAuth & Permissions"** and copy the **Bot User OAuth Token** (it starts with `xoxb-`).
7.  Go to **"Basic Information"**, scroll down to "App-Level Tokens", and generate a new token with the `connections:write` scope. Copy this token (it starts with `xapp-`).

### 2. Prepare Your API Keys

The bot requires environment variables for both Slack and your chosen LLM. You will provide these when you run the Docker container.

-   `SLACK_BOT_TOKEN`: Your bot's `xoxb-` token.
-   `SLACK_APP_TOKEN`: Your app's `xapp-` token.
-   `GEMINI_API_KEY` or `OPENAI_API_KEY`: Your LLM provider's API key.

## Building the Docker Image

From the root of the project directory, run the following command to build the Docker image:

```bash
docker build -t slack-bot-agent .
```

## Running the Bot

Use the `docker run` command to start your bot. The `-e` flag is used to pass your secret tokens and API keys to the container as environment variables.

```bash
docker run -d --name my-slack-bot \
  -e SLACK_BOT_TOKEN="xoxb-your-token-here" \
  -e SLACK_APP_TOKEN="xapp-your-token-here" \
  -e GEMINI_API_KEY="your-api-key-here" \
  slack-bot-agent
```

-   `-d` runs the container in detached (background) mode.
-   `--name my-slack-bot` assigns a memorable name to your container.
-   Replace the placeholder values with your actual tokens and keys.

## Logging

The bot logs all output to the container's console (stdout). To view the logs, use the `docker logs` command:

```bash
# View current logs
docker logs my-slack-bot

# Follow logs in real-time
docker logs -f my-slack-bot
```

## Project Structure

-   `slack_bot.py`: The main entry point that starts the Slack listener.
-   `slack_message_handler.py`: Handles incoming Slack mentions, processes the request, and sends the response.
-   `slack_agent.py`: Contains the core LLM agent logic, using `pydantic.ai` to interact with the language model.
-   `logger_config.py`: Configures console logging for the application.
-   `history/`: Directory where conversation history is stored as JSON files, one per channel. Note: This directory is ephemeral and will be lost if the container is removed or restarted.
-   `Dockerfile`: Defines the instructions for building the Docker image.
-   `requirements.txt`: Lists the Python dependencies.
-   `.dockerignore`: Specifies files to exclude from the Docker build.

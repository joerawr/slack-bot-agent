# AI Slack Bot

A conversational Slack bot powered by [`pydantic.ai`](https://ai.pydantic.dev) that answers questions and remembers channel-specific context. This project is designed to be run as a Docker container or deployed on Kubernetes.

## Features

-   **Conversational AI:** Responds to user questions and commands when mentioned in a channel.
-   **Channel-Specific Memory:** Maintains a separate conversation history for each channel, allowing for contextual follow-follow-up questions.
-   **Threaded Conversations:** Acknowledges requests and replies within threads to keep channels clean.
-   **Containerized:** Runs in a Docker container for easy and consistent deployment.

## Prerequisites

-   A Slack Workspace with permissions to create and install apps.
-   A Gemini, OpenAI, or other LLM API key.
-   **For Docker:** Docker installed and running on your system.
-   **For Kubernetes:** A running Kubernetes cluster and `kubectl` configured.

## Configuration: Slack App & API Keys

Before deploying, you need to configure the Slack App and get your API keys. These steps are required for both Docker and Kubernetes deployments.

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

The bot requires the following environment variables.

-   `SLACK_BOT_TOKEN`: Your bot's `xoxb-` token.
-   `SLACK_APP_TOKEN`: Your app's `xapp-` token.
-   `GEMINI_API_KEY` or `OPENAI_API_KEY`: Your LLM provider's API key.

## Deployment

You can run the bot using Docker directly or deploy it to a Kubernetes cluster.

### Option 1: Docker

This is the simplest way to run the bot on a single machine.

#### Using the Pre-built Image

A pre-built image is available on GitHub Container Registry. You can pull it directly:

```bash
docker pull ghcr.io/joerawr/slack-bot-agent:latest
```

#### Building the Image (Optional)

If you prefer to build the image yourself, run the following command from the project root:

```bash
docker build -t slack-bot-agent .
```

#### Running the Bot

Use the `docker run` command to start your bot. The `-e` flag is used to pass your secret tokens and API keys.

```bash
docker run -d --name my-slack-bot \
  -e SLACK_BOT_TOKEN="xoxb-your-token-here" \
  -e SLACK_APP_TOKEN="xapp-your-token-here" \
  -e GEMINI_API_KEY="your-api-key-here" \
  ghcr.io/joerawr/slack-bot-agent:latest
```

-   `-d` runs the container in detached (background) mode.
-   `--name my-slack-bot` assigns a memorable name to your container.
-   Replace the placeholder values with your actual tokens and keys.
-   **Note on History:** With this basic Docker command, the conversation history is stored inside the container and will be lost if the container is removed. For persistence, you would need to mount a volume to the `/app/history` directory.

#### Logging

To view the bot's logs, use the `docker logs` command:

```bash
# View current logs
docker logs my-slack-bot

# Follow logs in real-time
docker logs -f my-slack-bot
```

### Option 2: Kubernetes

Deploying to Kubernetes is recommended for production environments. It provides persistence for conversation history, automatic restarts, and scalability.

For detailed instructions on how to deploy the bot to a Kubernetes cluster, please see the **[Kubernetes Deployment Guide](./kubernetes.md)**.

## Project Structure

-   `slack_bot.py`: The main entry point that starts the Slack listener.
-   `slack_message_handler.py`: Handles incoming Slack mentions, processes the request, and sends the response.
-   `slack_agent.py`: Contains the core LLM agent logic, using `pydantic.ai` to interact with the language model.
-   `logger_config.py`: Configures console logging for the application.
-   `history/`: Directory where conversation history is stored as JSON files, one per channel.
-   `Dockerfile`: Defines the instructions for building the Docker image.
-   `requirements.txt`: Lists the Python dependencies.
-   `.dockerignore`: Specifies files to exclude from the Docker build.
-   `kubernetes.md`: A detailed guide for deploying the application to a Kubernetes cluster.
-   `slack-bot-pvc.yaml`, `slack-bot-deployment.yaml`: Example Kubernetes manifest files.

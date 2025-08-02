# PRD: Pydantic.ai Slack Bot

**Version:** 1.2

**Date:** 2025-08-02

## 1. Overview

This document outlines the requirements for a Slack bot that integrates with a Large Language Model (LLM) using the `pydantic.ai` framework. The bot will serve as a conversational agent within a Slack workspace, responding to user prompts.

## 2. Objective

The primary goal is to create a simple, functional Slack bot that can be mentioned by users to ask questions or give commands to an LLM such as OpenAI or Gemini. This provides a foundation for more complex interactions and integrations with other services in the future.

## 3. Core Features (MVP)

### 3.1. Slack Integration

-   The bot will connect to Slack using Socket Mode.
-   The bot will listen for `app_mention` events in any channel it is a member of.
-   It will ignore all other message types to prevent unintended responses.

### 3.2. Prompt Handling

-   When mentioned, the bot will extract the user's message text, excluding the bot's own `@mention`.
-   This extracted text will be treated as the prompt for the LLM.
-   The bot will post a temporary "Thinking..." message in a thread to acknowledge receipt of the request.

### 3.3. LLM Interaction

-   The extracted prompt is passed as a command-line argument to a Python script (`slack_agent.py`).
-   This script uses the `pydantic.ai` library to interact with a [LLM model](https://ai.pydantic.dev/models). 
    - For example: `google-gla:gemini-2.5-flash`.
-   The agent has a system prompt: "Be concise, reply with one sentence."

### 3.4. Conversation History

-   The bot maintains a separate conversation history for each channel.
-   History is stored in JSON files within the `history/` directory (e.g., `history/<channel_id>.json`).
-   When a user interacts with the bot in a channel, the existing history for that channel is loaded and passed to the LLM, providing context for follow-up questions.
-   The new conversation turn (user prompt and bot response) is appended to the channel's history file.

### 3.5. Response Handling

-   The LLM's text response will be captured from the script's output.
-   The response will be formatted as a plain text message.
-   The final response will be posted in the same thread as the acknowledgment message.

### 3.6. Logging and Error Handling

-   All major actions (e.g., receiving a mention, invoking the agent, sending a response) will be logged to `logs/slack_bot.log` and `logs/slack_message_handler.log`.
-   Errors from the LLM agent script (e.g., API failures, exceptions) will be logged to `logs/slack_agent.log`.
-   In case of an error, a user-friendly error message will be posted to the Slack thread.

## 4. Technical Stack

-   **Language:** Python 3
-   **Core Framework:** `pydantic.ai`
-   **Slack Integration:** `slack-bolt`
-   **LLM:** Google Gemini (via `pydantic.ai`'s `google-gla` provider)
-   **Deployment:** The bot is run as a single process from the command line or as a Docker container.

## 5. Roadmap

### 5.1. Completed

-   **MVP:** Core functionality for Slack interaction and LLM responses.
-   **Containerization:** A Dockerfile is available for building and deploying the bot as a container.

### 5.2. Next Up

-   **MCP Tool Use:** Integrate with Model Context Protocol (MCPs) by implementing `pydantic.ai` tool use. This will allow the bot to perform actions by calling functions based on user requests. This will likely involve using `pydantic.ai`'s structured output and dependency injection features.

### 5.3. Future Ideas

-   **Interactive Components:** Add Slack buttons or menus for common commands.
-   **Direct Messages:** Allow users to interact with the bot in a DM channel.
-   **Advanced History Management:** Implement more sophisticated history controls, such as summarization or a sliding window, to manage token limits in long conversations.
-   **Structured Output:** Expand beyond plain text to handle structured data (e.g., Pydantic models, JSON) for more complex responses.

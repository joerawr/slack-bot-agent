#!/usr/bin/env python3
"""
Slack LLM Bot - Main Entry Point

This script initializes the Slack bot that listens for mentions, processes
requests with a Pydantic.ai agent, and sends the results back to Slack.
"""

import os
import sys
import threading
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_message_handler import process_slack_mention
from logger_config import setup_logger

# Set up logging
logger = setup_logger('slack_bot')

def start_slack_bot():
    """Initialize and start the Slack bot"""
    # Get tokens from environment
    slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_app_token = os.environ.get("SLACK_APP_TOKEN")
    
    if not slack_bot_token or not slack_app_token:
        logger.error("Missing required Slack tokens. Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN environment variables.")
        print("Error: Missing required Slack tokens")
        print("Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN environment variables")
        return
        
    # Generate a unique session ID to track this bot instance
    session_id = f"bot-{int(time.time())}"
    logger.info(f"Starting Slack LLM Bot - Session ID: {session_id}")
    
    # Initialize the Slack Bolt app
    app = App(token=slack_bot_token)
    
    # Handler for app_mentions event
    @app.event("app_mention")
    def handle_app_mentions(event, say, client):
        """When someone mentions the bot in a channel"""
        channel = event["channel"]
        user = event["user"]
        text = event["text"]
        
        # Clear log message to identify this mention
        mention_id = f"mention-{int(time.time()*1000)}"
        logger.info(f"[{session_id}][{mention_id}] Received mention from user {user} in channel {channel}")
        logger.info(f"[{session_id}][{mention_id}] Message text: '{text}'")
        
        # Start processing in a separate thread to avoid blocking
        threading.Thread(
            target=process_slack_mention,
            args=(client, event, say, session_id, mention_id),
            daemon=True
        ).start()
    
    # Message event handler - check if we have any other handlers that might respond
    @app.event("message")
    def handle_message_events(body, logger):
        # This is a fallback handler. We don't expect it to be triggered if the bot is only mentioned.
        # logger.info(f"[{session_id}] Generic message event received: {body['event']['text']}")
        pass

    # Start the app using Socket Mode
    logger.info(f"[{session_id}] Starting Slack bot in Socket Mode")
    print(f"Starting Slack LLM Bot in Socket Mode - Session ID: {session_id}")
    print("Waiting for mentions... (Press Ctrl+C to quit)")
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()

if __name__ == "__main__":
    # Check for any existing bot processes
    try:
        import psutil
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['pid'] != current_pid and 'python' in proc.info['name']:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'slack_bot.py' in cmdline:
                    logger.warning(f"Another slack_bot.py process detected: PID {proc.info['pid']}")
                    print(f"WARNING: Another slack_bot.py process might be running (PID {proc.info['pid']})")
    except ImportError:
        logger.info("psutil not installed, skipping process check")
    except Exception as e:
        logger.warning(f"Could not check for existing processes: {e}")

    # Start the Slack bot
    start_slack_bot()
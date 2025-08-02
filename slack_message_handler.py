"""
Slack Message Handler

This module handles processing of Slack mentions, passes them to the LLM agent,
and sends responses back to Slack channels.
"""
import re
import os
import sys
import subprocess
from slack_message_formatter import format_for_slack
from logger_config import setup_logger

# Set up logging
logger = setup_logger('slack_message_handler', 'logs/slack_message_handler.log')

def extract_request(text: str) -> str:
    """
    Extract the actual request from a Slack message.
    
    Args:
        text: The raw Slack message text
        
    Returns:
        The extracted user prompt
    """
    # Remove the bot mention from the text
    # Example: "<@U12345> Tell me a joke" -> "Tell me a joke"
    mention_pattern = r'<@[A-Z0-9]+>'
    request = re.sub(mention_pattern, '', text).strip()
    return request

def process_slack_mention(client, event, say, session_id="unknown", mention_id="unknown"):
    """
    Process a Slack mention event, run the LLM agent, and respond in the channel.
    
    Args:
        client: The Slack client
        event: The mention event data
        say: The say function to respond in the channel
        session_id: Unique ID for the bot session
        mention_id: Unique ID for this mention
    """
    channel = event.get("channel", "unknown")
    user = event.get("user", "unknown")
    text = event.get("text", "")
    ts = event.get("ts", "")  # Message timestamp for threading
    
    # Log information about this mention
    logger.info(f"[{session_id}][{mention_id}] Processing mention in channel {channel} from user {user}")
    
    # Extract the actual request
    request = extract_request(text)
    logger.info(f"[{session_id}][{mention_id}] Extracted request: '{request}'")
    
    # Ensure we have a non-empty request
    if not request:
        logger.info(f"[{session_id}][{mention_id}] Empty request, sending default response")
        say(text="Hello! How can I help you today?", thread_ts=ts)
        return
    
    # Send an acknowledgment message to show we're responding
    ack_text = f"Thinking about your request: `{request}`..."
    logger.info(f"[{session_id}][{mention_id}] Sending acknowledgment: '{ack_text}'")
    say(text=ack_text, thread_ts=ts)
    
    try:
        # Create a directory for history if it doesn't exist
        history_dir = os.path.join(os.path.dirname(__file__), 'history')
        os.makedirs(history_dir, exist_ok=True)
        history_file = os.path.join(history_dir, f"{channel}.json")

        # Process the request by invoking the slack_agent.py script
        logger.info(f"[{session_id}][{mention_id}] Invoking slack_agent.py for request with history file: {history_file}")
        
        # Call the script with the user's request as a single argument
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'slack_agent.py'), request, "--history-file", history_file]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        result = proc.stdout.strip()

    except subprocess.CalledProcessError as e:
        error_message = f"Error processing your request. The agent script failed."
        logger.error(f"[{session_id}][{mention_id}] Error running slack_agent.py: {e.stderr}")
        say(text=f"{error_message}\n> {e.stderr}", thread_ts=ts)
        return
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.error(f"[{session_id}][{mention_id}] {error_message}", exc_info=True)
        say(text=error_message, thread_ts=ts)
        return

    # Format and send the response
    formatted_response = format_for_slack(result)
    logger.info(f"[{session_id}][{mention_id}] Sending response of length {len(formatted_response)}")
    say(text=formatted_response, thread_ts=ts)
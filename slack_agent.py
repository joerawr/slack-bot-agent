from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
import argparse
import sys
import os
from logger_config import setup_logger

# Set up logging
logger = setup_logger('slack_agent', 'logs/slack_agent.log')

def run_agent(prompt: str, history_file: str = None):
    """
    Initializes and runs the Pydantic AI agent.
    """
    history: list[ModelMessage] = []
    if history_file and os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history_json = f.read()
        if history_json:
            history = ModelMessagesTypeAdapter.validate_json(history_json)

    try:
        # Define a very simple agent including the model to use
        agent = Agent(
            'google-gla:gemini-2.5-flash',
            # Register a static system prompt
            system_prompt='Be concise, reply with one sentence.',
        )

        # Run the agent synchronously
        result = agent.run_sync(prompt, message_history=history)
        print(result.output)

        if history_file:
            with open(history_file, 'w') as f:
                f.write(ModelMessagesTypeAdapter.dump_json(result.all_messages()).decode())

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        # Also print to stderr so the calling process can capture it
        print(f"Error: Agent execution failed. Check logs/slack_agent.log for details.", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Main function to parse arguments and run the agent.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run a simple Pydantic AI agent with a given prompt.")
    parser.add_argument("prompt", help="The prompt to send to the agent.")
    parser.add_argument("--history-file", help="Path to the conversation history file (JSON).")
    args = parser.parse_args()
    
    run_agent(args.prompt, args.history_file)

if __name__ == "__main__":
    main()
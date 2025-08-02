"""
Slack Message Formatter

This module handles formatting of LLM output for Slack messages.
"""

def format_for_slack(content: str) -> str:
    """
    Format LLM output for Slack.
    
    Args:
        content: The output content from the LLM.
        
    Returns:
        Formatted message ready for Slack.
    """
    # Content is returned as-is for a more conversational feel.
    # The previous implementation wrapped it in ``` for code blocks.
    return content
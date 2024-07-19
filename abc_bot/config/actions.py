from typing import Optional
from nemoguardrails.actions import action

# Custom output rail: List of proprietary words that we want to make sure do not appear in the output
@action(is_system_action = True)
async def check_blocked_terms(context: Optional[dict] = None):
    bot_response = context.get("bot_message")

    # A quick hard-coded list of proprietary terms. You can also read from a file.
    proprietary_terms = ["Magazine", "Cybersecurity", "Proprietary", "Quantum", "Nuclear"]

    for term in proprietary_terms:
        if term in bot_response.lower():
            return True
    
    return False
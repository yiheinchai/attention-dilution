import re
from . import config

def evaluate_response(response_text: str) -> dict:
    """
    Evaluates the LLM response based on criteria defined in config.py.
    Returns a dictionary of boolean checks and an overall score.
    """
    if response_text is None:
        # Handle cases where LLM interaction failed
        return {
            "response_received": False,
            "starts_with_phrase": False,
            "uses_numbered_list": False,
            "avoids_forbidden_words": False,
            "formal_tone_check": False, # Placeholder
            "adherence_score": 0,
            "total_possible_score": 4 # Adjust if more checks are added
        }

    results = {"response_received": True}
    score = 0
    possible_score = 0 # Track how many checks are active

    # 1. Check Start Phrase
    possible_score += 1
    starts_correctly = response_text.startswith(config.EXPECTED_START_PHRASE)
    results["starts_with_phrase"] = starts_correctly
    if starts_correctly:
        score += 1

    # 2. Check Numbered List Format (simple check: looks for lines starting with number+dot+space)
    possible_score += 1
    # Regex to find lines starting with digits, a dot, and whitespace
    numbered_list_pattern = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
    uses_numbered_list = bool(numbered_list_pattern.search(response_text))
    results["uses_numbered_list"] = uses_numbered_list
    if uses_numbered_list:
        score += 1
    # More robust check could involve parsing list items

    # 3. Check Forbidden Words
    possible_score += 1
    found_forbidden = False
    response_lower = response_text.lower()
    for word in config.FORBIDDEN_WORDS:
        if word.lower() in response_lower:
            found_forbidden = True
            break
    results["avoids_forbidden_words"] = not found_forbidden
    if not found_forbidden:
        score += 1

    # 4. Check Formal Tone (Basic Placeholder - Very difficult to automate reliably)
    # This is a simplified check. Real tone evaluation often needs human raters or more sophisticated NLP.
    possible_score += 1
    informal_markers = ["i think", "i feel", "don't", "can't", "it's", "you know", "actually", "just"] # Example markers
    found_informal = any(marker in response_lower for marker in informal_markers)
    # You might add checks for excessive exclamation points, etc.
    results["formal_tone_check"] = not found_informal # Assuming formality means *avoiding* these
    if not found_informal:
         score += 1


    results["adherence_score"] = score
    results["total_possible_score"] = possible_score

    return results

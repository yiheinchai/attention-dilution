from . import utils
from . import config

def generate_user_input(full_filler_text: str, core_query: str, target_total_user_tokens: int, model_name: str) -> str:
    """
    Generates the user input string by combining filler text and the core query
    to meet the target total token count. Places query at the end.
    """
    tokenizer = utils.get_tokenizer(model_name)
    query_tokens = utils.count_tokens(core_query, model_name)

    required_filler_tokens = target_total_user_tokens - query_tokens
    if required_filler_tokens < 0:
        print(f"Warning: Core query ({query_tokens} tokens) is longer than target total user tokens ({target_total_user_tokens}). Using query only.")
        # Optionally, truncate query? For now, just use the query.
        return utils.get_token_limited_text(core_query, target_total_user_tokens, model_name)

    # Get the precisely token-limited filler text
    filler_text_segment = utils.get_token_limited_text(full_filler_text, required_filler_tokens, model_name)

    # Combine filler and query
    user_input = filler_text_segment + "\n\n" + core_query # Add separator

    # Final check - can sometimes be off by a few tokens due to encoding nuances
    final_token_count = utils.count_tokens(user_input, model_name)
    if abs(final_token_count - target_total_user_tokens) > 5: # Allow small tolerance
         print(f"Warning: Generated user input token count ({final_token_count}) differs significantly from target ({target_total_user_tokens}).")

    # print(f"Debug: Target User Tokens: {target_total_user_tokens}, Query Tokens: {query_tokens}, Required Filler: {required_filler_tokens}, Actual Filler Tokens: {utils.count_tokens(filler_text_segment, model_name)}, Final Input Tokens: {final_token_count}")

    return user_input

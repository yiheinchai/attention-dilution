import tiktoken
import os

# --- Tokenizer Cache ---
_tokenizer_cache = {}

def get_tokenizer(model_name: str):
    """Gets a tiktoken tokenizer for the specified model, caching it for efficiency."""
    if model_name not in _tokenizer_cache:
        try:
            print(f"Loading tokenizer for model: {model_name}")
            _tokenizer_cache[model_name] = tiktoken.encoding_for_model(model_name)
        except KeyError:
            print(f"Warning: No exact tokenizer found for model '{model_name}'. Falling back to 'cl100k_base'.")
            _tokenizer_cache[model_name] = tiktoken.get_encoding("cl100k_base")
    return _tokenizer_cache[model_name]

def count_tokens(text: str, model_name: str) -> int:
    """Counts the number of tokens in a string for a given model."""
    if not text:
        return 0
    tokenizer = get_tokenizer(model_name)
    return len(tokenizer.encode(text))

def get_token_limited_text(full_text: str, max_tokens: int, model_name: str) -> str:
    """
    Truncates text to be at most max_tokens long, using the specified model's tokenizer.
    Attempts to be precise with token count.
    """
    if max_tokens <= 0:
        return ""

    tokenizer = get_tokenizer(model_name)
    tokens = tokenizer.encode(full_text)

    if len(tokens) <= max_tokens:
        return full_text # Return original if already short enough
    else:
        # Truncate the token list and decode back to text
        truncated_tokens = tokens[:max_tokens]
        truncated_text = tokenizer.decode(truncated_tokens)
        # Double-check token count after decoding (sometimes decoding adds/removes tokens slightly)
        # Re-encode and slice if necessary for absolute precision (optional, but good)
        final_tokens = tokenizer.encode(truncated_text)
        if len(final_tokens) > max_tokens:
             # Slice again if decoding made it longer
             truncated_text = tokenizer.decode(final_tokens[:max_tokens])
        elif len(final_tokens) < max_tokens:
             # This might happen if decoding merged some tokens. Usually minor.
             pass # Accept slightly shorter text

        return truncated_text

def load_text_file(filepath: str) -> str | None:
    """Loads text content from a file."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

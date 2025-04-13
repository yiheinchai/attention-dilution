import time
from openai import OpenAI, RateLimitError, APIError
from . import config

# Initialize OpenAI client (respects OPENAI_API_KEY environment variable)
# Ensure API_KEY is set in config or environment before this runs
client = OpenAI(api_key=config.API_KEY)

def get_llm_response(system_prompt: str, user_input: str, model_name: str, temperature: float, max_retries: int = 3, retry_delay: int = 5) -> str | None:
    """
    Gets a response from the specified LLM model using the OpenAI API.
    Includes basic retry logic for rate limits.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    attempt = 0
    while attempt < max_retries:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=config.MAX_OUTPUT_TOKENS
            )
            # print(response.choices[0].message.content) # Debug print
            return response.choices[0].message.content.strip()

        except RateLimitError as e:
            attempt += 1
            print(f"Rate limit exceeded. Retrying in {retry_delay}s... (Attempt {attempt}/{max_retries})")
            if attempt >= max_retries:
                print("Max retries reached for rate limit.")
                return None
            time.sleep(retry_delay)
        except APIError as e:
            attempt += 1
            print(f"API error occurred: {e}. Retrying in {retry_delay}s... (Attempt {attempt}/{max_retries})")
            if attempt >= max_retries:
                print("Max retries reached for API error.")
                return None
            time.sleep(retry_delay)
        except Exception as e:
            print(f"An unexpected error occurred during API call: {e}")
            return None # Don't retry on unexpected errors immediately

    return None # Should not be reached if retry logic is correct, but safety return

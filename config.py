import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional, good practice)
load_dotenv()

# --- API Configuration ---
# Best practice: Load API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set.")
    # You might fall back to a hardcoded key here for simple testing,
    # BUT DO NOT COMMIT IT TO VERSION CONTROL.
    # API_KEY = "your-api-key-here" # <-- NOT RECOMMENDED FOR PRODUCTION/SHARING

# --- Model Configuration ---
MODEL_NAME = "gpt-3.5-turbo" # Example: Use a model that supports your required context length
# MODEL_NAME = "gpt-4-turbo-preview" # Example for larger context
# MODEL_NAME = "claude-3-opus-20240229" # Example for Anthropic (requires different library/interaction)

# --- Experiment Parameters ---
SYSTEM_PROMPT = """
You are 'ResearchBot Alpha'. Your primary function is to process the user's text and follow instructions precisely. Your responses must adhere strictly to the following rules:
1.  **Start Phrase:** Every response MUST begin with the exact phrase: "ResearchBot Alpha Analysis:". No variations allowed.
2.  **Output Format:** Present findings as a numbered list (e.g., "1. Finding one."). Do not use bullet points (*, -) or any other format.
3.  **Tone and Style:** Maintain a strictly formal and objective tone. Avoid any informal language, contractions, or expressions of opinion/emotion. Your persona is that of a detached analytical engine.
4.  **Negative Constraint:** Absolutely DO NOT use the word "significant" or any of its variations (significantly, significance). Find synonyms if needed (e.g., substantial, considerable, noteworthy, important).
5.  **Conciseness:** Keep explanations brief and to the point. Focus on direct answers to the user's request based *only* on the provided text.
6.  **Handling Missing Info:** If the text doesn't contain information to fulfill a request, state "Information not found in provided text." Do not speculate.

Adhere to all these rules consistently in your output. Process the user text that follows.
"""

CORE_QUERY = "Based on the provided text, identify the main challenges discussed regarding renewable energy adoption."

# --- Input Data Configuration ---
FILLER_TEXT_PATH = "data/filler_text.txt"

# --- Experiment Design ---
# Define the different user input lengths (in tokens) to test
# Ensure these are feasible within the chosen model's context window,
# considering system prompt, query, and expected output length.
USER_INPUT_TOKEN_LENGTHS = [500, 2000, 8000] # Example lengths
NUM_TRIALS = 3 # Number of times to run the experiment for each length

# --- Output Configuration ---
RESULTS_DIR = "results"
RESULTS_FILENAME = "experiment_results.json"

# --- Evaluation Criteria ---
# These should match the rules in the SYSTEM_PROMPT
EXPECTED_START_PHRASE = "ResearchBot Alpha Analysis:"
FORBIDDEN_WORDS = ["significant", "significantly", "significance"]
# Add more criteria checks as needed (e.g., regex for numbered list)

# --- LLM Call Parameters ---
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 500 # Set a reasonable limit for the response length

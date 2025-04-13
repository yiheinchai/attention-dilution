import os
import json
import time
from . import config
from . import utils
from . import input_generator
from . import llm_interaction
from . import evaluation

def main():
    print("Starting Attention Dilution Experiment...")

    # --- Setup ---
    # Ensure results directory exists
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    results_filepath = os.path.join(config.RESULTS_DIR, config.RESULTS_FILENAME)

    # Load the entire filler text corpus once
    print(f"Loading filler text from: {config.FILLER_TEXT_PATH}")
    full_filler_text = utils.load_text_file(config.FILLER_TEXT_PATH)
    if full_filler_text is None:
        print("Failed to load filler text. Exiting.")
        return
    filler_token_count = utils.count_tokens(full_filler_text, config.MODEL_NAME)
    print(f"Loaded filler text: {filler_token_count} tokens.")


    # --- Experiment Loop ---
    all_results = []
    total_runs = len(config.USER_INPUT_TOKEN_LENGTHS) * config.NUM_TRIALS
    current_run = 0

    for length in config.USER_INPUT_TOKEN_LENGTHS:
        print(f"\n--- Testing User Input Length: {length} tokens ---")

        if length > filler_token_count + utils.count_tokens(config.CORE_QUERY, config.MODEL_NAME):
             print(f"Warning: Target length {length} is greater than available filler text + query. Skipping this length.")
             total_runs -= config.NUM_TRIALS # Adjust total runs count
             continue

        for trial in range(1, config.NUM_TRIALS + 1):
            current_run += 1
            print(f"--- Running Trial {trial}/{config.NUM_TRIALS} for {length} tokens ({current_run}/{total_runs}) ---")
            start_time = time.time()

            # 1. Generate Input
            print("Generating user input...")
            user_input = input_generator.generate_user_input(
                full_filler_text=full_filler_text,
                core_query=config.CORE_QUERY,
                target_total_user_tokens=length,
                model_name=config.MODEL_NAME
            )
            actual_input_tokens = utils.count_tokens(user_input, config.MODEL_NAME)
            system_prompt_tokens = utils.count_tokens(config.SYSTEM_PROMPT, config.MODEL_NAME)
            total_prompt_tokens = system_prompt_tokens + actual_input_tokens
            print(f"Generated user input: {actual_input_tokens} tokens.")
            print(f"Total prompt tokens (system + user): {total_prompt_tokens}")


            # 2. Get LLM Response
            print("Querying LLM...")
            raw_response = llm_interaction.get_llm_response(
                system_prompt=config.SYSTEM_PROMPT,
                user_input=user_input,
                model_name=config.MODEL_NAME,
                temperature=config.TEMPERATURE
            )

            if raw_response is None:
                print("Failed to get LLM response for this trial.")
                eval_results = evaluation.evaluate_response(None) # Get failure evaluation
            else:
                # 3. Evaluate Response
                print("Evaluating response...")
                eval_results = evaluation.evaluate_response(raw_response)
                print(f"Evaluation Score: {eval_results.get('adherence_score', 'N/A')}/{eval_results.get('total_possible_score', 'N/A')}")


            # 4. Store Result
            trial_result = {
                "input_length_target": length,
                "trial_number": trial,
                "model_name": config.MODEL_NAME,
                "system_prompt_tokens": system_prompt_tokens,
                "user_input_actual_tokens": actual_input_tokens,
                "total_prompt_tokens": total_prompt_tokens,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": round(time.time() - start_time, 2),
                # Storing the full prompts/responses can make the file huge for large inputs
                # Consider storing only hashes or omitting for very large runs if space is an issue
                # "system_prompt": config.SYSTEM_PROMPT,
                # "user_input": user_input,
                "raw_response": raw_response if raw_response is not None else "ERROR: No response received",
                "evaluation": eval_results
            }
            all_results.append(trial_result)

            # Save incrementally (optional, good for long runs)
            try:
                with open(results_filepath, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, indent=4)
            except Exception as e:
                 print(f"Error saving results incrementally: {e}")

            # Optional delay between trials to avoid rate limits further
            # time.sleep(1)


    # --- Save Final Results ---
    print(f"\nExperiment finished. Saving final results to {results_filepath}")
    try:
        with open(results_filepath, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=4)
        print("Results saved successfully.")
    except Exception as e:
        print(f"Error saving final results: {e}")

if __name__ == "__main__":
    # Ensure API key is available before starting
    if not config.API_KEY:
         print("\nError: OpenAI API key not found.")
         print("Please set the OPENAI_API_KEY environment variable or configure it in config.py (not recommended for sharing).")
    else:
         main()

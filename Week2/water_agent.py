import re
import json
from typing import List
from water_tools import TOOL_REGISTRY

# ReAct Agent for Water Meter Transcription
# --------------------------------------------
def water_meter_transcription_agent(water_input: str, water_json: List[dict], logs: List[str]) -> None:
    
    logs.append(f"Thought: Clean the input before extracting anything from: '{water_input}'")

    # 1. Clean text
    logs.append("Action: Call tool 'clean_text'")
    cleaned = TOOL_REGISTRY['clean_text']['function'](water_input)
    logs.append(f"Observation: Cleaned text: '{cleaned}'")

    # 2. Normalize unit wording
    logs.append("Thought: Standardize unit wording so the extractor can operate more reliably.")
    logs.append("Action: Call tool 'unit_normalizer'")
    normalized_input = TOOL_REGISTRY['unit_normalizer']['function'](cleaned)
    logs.append(f"Observation: Normalized input: '{normalized_input}'")

    # 3. Extract unit and reading
    logs.append("Thought: Now that the text is normalized, I should extract the unit ID and reading.")
    logs.append("Action: Call tool 'extract_unit_and_reading'")
    unit_candidate, reading_candidate = TOOL_REGISTRY["extract_unit_and_reading"]["function"](normalized_input)
    logs.append(f"Observation: extractor returned -> unit={unit_candidate}, reading={reading_candidate}")

    if unit_candidate and reading_candidate:
        # 4: Standardize Unit ID
        logs.append("Thought: Format the extracted unit ID into a consistent representation.")
        logs.append("Action: Call tool 'standardize_unit_id'")
        standardized_unit = TOOL_REGISTRY["standardize_unit"]["function"](unit_candidate)
        logs.append(f"Observation: Standardized unit ID: '{standardized_unit}'")

        # 5. Validate reading
        logs.append("Thought: Verify that the extracted reading is numeric and valid.")
        logs.append(f"Action: Call tool 'validate_reading' on {reading_candidate}")
        is_valid, numeric_reading = TOOL_REGISTRY["validate_reading"]["function"](reading_candidate)
        logs.append(f"Observation: validate_reading → valid={is_valid}, numeric={numeric_reading}")

        if not is_valid:
            logs.append("Observation: invalid reading — skipping entry.")
            return
        
        # 6. Check for duplicates
        logs.append("Thought: Ensure we do not add the same unit twice. Check for duplicates.")
        logs.append("Action: Call tool 'duplicate_checker'")
        is_dup = TOOL_REGISTRY["duplicate_checker"]["function"](standardized_unit, water_json)
        logs.append(f"Observation: duplicate_checker → is_duplicate={is_dup}")

        if is_dup:
            logs.append(f"Observation: Unit {standardized_unit} already exists — skipping")
            return
        
        # 7 — Append to JSON
        logs.append("Thought: Append the validated entry to the water JSON.")
        logs.append(f"Action: append {{unit: {standardized_unit}, reading: {numeric_reading}}} to JSON")
        water_json.append({"unit": standardized_unit, "reading": numeric_reading})
        logs.append(f"Observation: JSON now → {water_json}")

    elif not unit_candidate or not reading_candidate:
        logs.append("Observation: Missing unit or reading — cannot proceed with this entry.")


# Helper function to parse user input into parts
# ----------------------------------------------
def parse_input(user_input: str) -> List[str]:
    parts = re.split(r"[,\.\n]+", user_input)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


# ---------------------------
# Main Execution
def main():
    # User input for water meter 
    print("Enter the water meter reading (sample input: Unit 19A reads 30 cubic meter, 19B is 5 cubic meter, 19C reads 8.)")
    water_reading = input("Water meter reading: ")

    water_json = []
    logs: List[str] = []
    logs.append(f"Thought: Received user input. I need to extract units and readings from: '{water_reading}'")
    logs.append("Action: Agent Start = Tool-using ReAct agent for water meter reading.")
    logs.append("Observation: Printing Tool Summary:")
    for name, meta in TOOL_REGISTRY.items():
        logs.append(f"- {name}: {meta['purpose']}")
    print("----------------------------\n")
    # Process each part of the input
    for water_input in parse_input(water_reading):
        water_meter_transcription_agent(water_input, water_json, logs)
    
    logs.append("Final Thought: Completed processing all water meter readings.")

    print("Water Meter JSON Output:", water_json)
    print("\nReAct Agent Logs:")
    for log in logs:
        print(log)

if __name__ == "__main__":
    main()

    




import re
from typing import List
from water_tools import TOOL_REGISTRY

# ---------------------------
# ReAct Agent for Water Meter Transcription
# ---------------------------
def water_meter_transcription_agent(water_input: str, water_json: List[dict], logs: List[str]) -> None:
    
    # 1. Clean text — always useful first
    if water_input.strip() == "":
        logs.append(f"Thought: Input is empty — no cleaning or extraction needed: '{water_input}'")
    elif re.search(r"\d", water_input) or re.search(r"[A-Za-z]", water_input):
        logs.append(f"Thought: Input contains potential unit IDs or readings — will clean and extract: '{water_input}'")
    else:
        logs.append(f"Thought: Input has no recognizable units or readings — skipping: '{water_input}'")
    logs.append("Action: Call tool 'clean_text'")
    cleaned = TOOL_REGISTRY['clean_text']['function'](water_input)
    logs.append(f"Observation: Cleaned text: '{cleaned}'")

    # 2. Normalize unit wording — only if unit-like words present
    if any(word in cleaned.lower() for word in ['cu m', 'm3', 'cubic meter', 'meter', 'metre']):
        logs.append("Thought: Detected unit-related words — normalize unit wording.")
        logs.append("Action: Call tool 'unit_normalizer'")
        normalized_input = TOOL_REGISTRY['unit_normalizer']['function'](cleaned)
        logs.append(f"Observation: Normalized input: '{normalized_input}'")
    else:
        logs.append("Thought: No unit-related words detected — skipping normalization.")
        normalized_input = cleaned

    # 3. Extract unit and reading
    logs.append("Thought: Extract unit and reading only if text seems to contain both.")
    logs.append("Action: Call tool 'extract_unit_and_reading'")
    unit_candidate, reading_candidate = TOOL_REGISTRY["extract_unit_and_reading"]["function"](normalized_input)
    logs.append(f"Observation: extractor returned -> unit={unit_candidate}, reading={reading_candidate}")

    if unit_candidate:
        # 4. Standardize Unit ID
        logs.append("Thought: Standardize the unit ID only if unit was found.")
        logs.append("Action: Call tool 'standardize_unit_id'")
        standardized_unit = TOOL_REGISTRY["standardize_unit"]["function"](unit_candidate)
        logs.append(f"Observation: Standardized unit ID: '{standardized_unit}'")
    else:
        standardized_unit = None

    if reading_candidate:
        # 5. Validate reading
        logs.append("Thought: Validate the reading only if a numeric value was extracted.")
        logs.append(f"Action: Call tool 'validate_reading' on {reading_candidate}")
        is_valid, numeric_reading = TOOL_REGISTRY["validate_reading"]["function"](reading_candidate)
        logs.append(f"Observation: validate_reading → valid={is_valid}, numeric={numeric_reading}")
        if not is_valid:
            logs.append("Observation: Invalid reading — skipping entry.")
            return
    else:
        logs.append("Observation: No reading found — cannot proceed with this entry.")
        return

    # 6. Check for duplicates — only if unit was found and standardized
    if standardized_unit:
        logs.append("Thought: Check for duplicates to prevent overwriting existing entries.")
        logs.append("Action: Call tool 'duplicate_checker'")
        is_dup = TOOL_REGISTRY["duplicate_checker"]["function"](standardized_unit, water_json)
        logs.append(f"Observation: duplicate_checker → is_duplicate={is_dup}")
        if is_dup:
            logs.append(f"Observation: Unit {standardized_unit} already exists — skipping")
            return
    else:
        logs.append("Observation: No unit ID — cannot check duplicates.")
        return

    # 7. Append to JSON
    logs.append("Thought: All checks passed — append the entry to JSON.")
    logs.append(f"Action: append {{unit: {standardized_unit}, reading: {numeric_reading}}} to JSON")
    water_json.append({"unit": standardized_unit, "reading": numeric_reading})
    logs.append(f"Observation: JSON now → {water_json}")


# ---------------------------
# Helper function to parse user input into parts
# ---------------------------
def parse_input(user_input: str) -> List[str]:
    parts = re.split(r"[,\.\n]+", user_input)
    return [p.strip() for p in parts if p.strip()]


# ---------------------------
# Main Execution
# ---------------------------
def main():
    print("Enter the water meter reading (sample: Unit 19A reads 30 cubic meter, 19B is 5 cubic meter, 19C reads 8.)")
    water_reading = input("Water meter reading: ")

    water_json = []
    logs: List[str] = []
    logs.append(f"Thought: Received user input. Need to extract units and readings: '{water_reading}'")
    logs.append("Action: Agent Start = Tool-using ReAct agent for water meter reading.")
    logs.append("Observation: Tool Summary:")
    for name, meta in TOOL_REGISTRY.items():
        logs.append(f"- {name}: {meta['purpose']}")

    print("----------------------------\n")
    for water_input in parse_input(water_reading):
        water_meter_transcription_agent(water_input, water_json, logs)
    
    logs.append("Final Thought: Completed processing all water meter readings.")

    print("Water Meter JSON Output:", water_json)
    print("\nReAct Agent Logs:")
    for log in logs:
        print(log)


if __name__ == "__main__":
    main()

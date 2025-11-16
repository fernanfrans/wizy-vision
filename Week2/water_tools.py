import re 
from typing import List, Dict, Any, Tuple, Optional


# Tool 1: Clean text input
# ------------------------------

def clean_text(text: str) -> str:
    """Remove punctuation/noise and normalize whitespace."""
    cleaned = re.sub(r"[^\w\s\-\/]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

# Tool 2: Normalize unit words
# ------------------------------

UNIT_MAPPING = {
    "CUBIC METER": "cubic meter",
    "CUBIC METRE": "cubic meter",
    "CU M": "cubic meter",
    "M3": "cubic meter",
    "M": "meter"
}

def unit_normalizer(unit_str: str) -> str:
    """Normalize unit representation (e.g., 'cu m' → 'cubic meter')."""
    upper_unit = unit_str.upper()
    return UNIT_MAPPING.get(upper_unit, unit_str.lower())

# Tool 3: Extract unit and reading
# ------------------------------

def extract_unit_and_reading(text: str):
    # Extract unit
    unit_match = re.search(
        r"(?:Unit\s*)?(\d+\s*[A-Za-z]|\d+[A-Za-z]?|\d+\-\w+)",
        text,
        re.IGNORECASE,
    )
    unit = unit_match.group(1).replace(" ", "") if unit_match else None

    # Extract reading using multiple strategies
    # strat 1. Keyword-based reading
    keyword_match = re.search(
        r"(?:reads|is|=|at|shows|indicates|reading)\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if keyword_match:
        return unit, keyword_match.group(1)

    # strat 2. Number followed by unit words
    unitword_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:cubic\s*meter|cu\s*m|m3|meter|metre)",
        text,
        re.IGNORECASE,
    )
    if unitword_match:
        return unit, unitword_match.group(1)

    # strat 3. Just a number 
    all_numbers = re.findall(r"\d+(?:\.\d+)?", text)

    if unit:
        unit_number = re.findall(r"\d+", unit)
        if unit_number:
            all_numbers = [n for n in all_numbers if n != unit_number[0]]

    if all_numbers:
        return unit, all_numbers[-1]

    return unit, None


# Tool 4: Standardize Unit ID
# ------------------------------

def standardize_unit_id(unit_id: str) -> str:
    """Standardize unit ID (e.g., '19a' → '19A', '19-A' → '19A')."""
    u = unit_id.upper()
    u = re.sub(r"[^0-9A-Z]", "", u)
    return u


# Tool 5: Validate reading
# ------------------------------

def validate_reading(
    value: str,
    min_allowed: int = 0,
    max_allowed: int = 99999
) -> Tuple[bool, Optional[int]]:
    """Check numeric range and convert to int."""
    try:
        v = int(value)
    except:
        return False, None

    if v < min_allowed or v > max_allowed:
        return False, v

    return True, v

# Tool 6: Duplicate detection 
# ------------------------------

def duplicate_checker(unit: str, water_json: List[Dict[str, Any]]) -> bool:
    existing_units = {entry["unit"] for entry in water_json}
    return unit in existing_units


# ---------------------------
# Tool Registry (metadata)
# ---------------------------

TOOL_REGISTRY = {
    "clean_text": {
        "function": clean_text,
        "purpose": "Removes noise and normalizes whitespace.",
        "when_to_use": "Always before parsing user text."
    },
    "unit_normalizer": {
        "function": unit_normalizer,
        "purpose": "Standardizes unit wording (cu m → cubic meter).",
        "when_to_use": "Before regex extraction."
    },
    "extract_unit_and_reading": {
        "function": extract_unit_and_reading,
        "purpose": "Extracts unit ID and numeric reading using regex.",
        "when_to_use": "After cleaning and normalizing."
    },
    "standardize_unit": {
        "function": standardize_unit_id,
        "purpose": "Normalizes unit ID format.",
        "when_to_use": "After extraction."
    },
    "validate_reading": {
        "function": validate_reading,
        "purpose": "Ensures the reading is numeric and valid.",
        "when_to_use": "After extracting reading."
    },
    "duplicate_checker": {
        "function": duplicate_checker,
        "purpose": "Checks if the unit already exists.",
        "when_to_use": "Before appending to JSON."
    },
}
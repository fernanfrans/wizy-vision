# 💧 Water Meter Transcription ReAct Agent

This project implements a **ReAct-style tool-using agent** designed to accurately extract **Unit IDs** and **Water Meter Readings** from unstructured, noisy user input. By utilizing a chain of specialized, modular tools, the agent ensures robust extraction, normalization, and validation of critical meter data.

---

## 💡 Overview: The ReAct Transcription Pipeline

The system is structured as a transparent, two-file architecture that processes raw text into validated, structured JSON data.

### Core Agent Workflow

The ReAct agent processes text through the following sequential steps, logging its thought process at each stage:

1.  **Cleaning** noisy text (e.g., removing extra punctuation).
2.  **Normalizing** unit wording (e.g., standardizing `cu m` to `cubic meter`).
3.  **Extraction** of the Unit ID and the numeric reading.
4.  **Standardization** of the Unit ID format (e.g., ensuring uppercase).
5.  **Validation** of the numeric reading (ensuring it's within a valid range).
6.  **Duplicate Checking** to prevent redundant entries for the same unit.
7.  **Saving** the final, structured data to JSON format.

---

## ⚙️ Project Structure

The system consists of two main Python files:

### 1. Agent Script (`main_agent.py`)

This is the entry point for the application. It handles user interaction and drives the ReAct process.

* **Input Handling:** Receives raw user input (e.g., `Unit 19A reads 30 cubic meter, 19B is 5.`).
* **Segmentation:** Splits multi-entry sentences into manageable segments for individual processing.
* **Agent Execution:** Calls the ReAct agent to process each segment through the tool chain.
* **Output:** Prints the **Structured JSON output**, the **Step-by-step ReAct logs**, and a **Tool Usage Summary** for transparency.

### 2. Tools Script (`water_tools.py`)

This script holds the library of reusable, specialized functions that the ReAct agent calls.

| Tool Name | Purpose | Description |
| :--- | :--- | :--- |
| **`clean_text`** | Pre-processing | Removes punctuation, excessive noise, and normalizes whitespace. |
| **`unit_normalizer`** | Data Consistency | Converts diverse unit terms to a single standard form (e.g., `cu m` → `cubic meter`). |
| **`extract_unit_and_reading`** | Core Extraction | Uses regex heuristics to detect and extract the Unit ID and the numeric meter reading. |
| **`standardize_unit_id`** | Format Enforcement | Ensures Unit IDs follow a consistent, standardized format (e.g., uppercase letters). |
| **`validate_reading`** | Data Integrity | Ensures readings are numeric and fall within the defined valid range (e.g., 0 to 9999). |
| **`duplicate_checker`** | Quality Control | Checks if a Unit ID already exists in the final data structure to prevent duplicates. |

#### Tool Registry

All tools are mapped in a central **`TOOL_REGISTRY`** dictionary, which provides the agent with metadata, including the tool's reference function, a clear `purpose`, and specific guidance on `when_to_use`.

---

## 🧠 How the ReAct Agent Works

The agent operates by following a classic **Reasoning → Acting → Observing** loop, which generates a complete, transparent trace:

1.  **Thought:** The agent logs a **Thought** explaining the current state and its plan for the next step (e.g., "I need to clean the text first.").
2.  **Action:** It logs an **Action**, specifying which tool to call and the input (e.g., `Action: clean_text("...")`).
3.  **Observation:** It logs the **Observation**, which is the output of the executed tool (e.g., `Observation: The text is now clean.`).
4.  The loop repeats, moving the process forward until the goal (validated JSON data) is reached.

This process provides a transparent and auditable trail, which is useful for debugging and quality assurance.

---

## ▶️ Running the Agent

### Execution

Run the main script from your terminal:
python main_agent.py

You will be prompted to enter the data: Enter the water meter reading
Example Input: Unit 19A reads 30 cubic meter, 19B is 5, 19C reads 8.

### Sample Output
The script will output the following validated JSON structure, along with the full ReAct logs:
[
  {"unit": "19A", "reading": 30},
  {"unit": "19B", "reading": 5},
  {"unit": "19C", "reading": 8}
]

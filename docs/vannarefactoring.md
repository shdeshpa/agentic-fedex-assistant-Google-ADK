Here’s a COSTAR prompt designed specifically for Cursor IDE to refactor your existing vanna_ollama_sqlite_fedex.py file into a modular Python package while preserving functionality and optimizing for future MCP (Model Context Protocol) tool integration.

⸻

COSTAR PROMPT: Modular Refactor for Vanna FedEx SQLite Project

Context:
You currently have a single script vanna_ollama_sqlite_fedex.py that connects VannaAI (or Ollama) with an SQLite database (fedex_rates.db) to enable text-to-SQL querying of FedEx rate data.
This file likely includes logic for:
	•	Vanna model initialization and training
	•	SQL query generation
	•	SQLite connection and execution
	•	Streamlit or CLI interaction

You want to modularize this code for maintainability, performance (avoid retraining Vanna repeatedly), and future integration with MCP tools.

⸻

Objective:
Refactor the existing file into a clean, modular structure under a new folder Vanna/.
Ensure that:
	•	The functionality remains identical.
	•	Vanna model training only happens once, and the trained model can be reloaded efficiently.
	•	Each module has a single clear responsibility.
	•	The main entry point (e.g., Streamlit or CLI) imports modules cleanly.

⸻

Structure to Create:

Vanna/
│
├── __init__.py
├── config.py              # Environment variables, constants, model paths
├── model_manager.py       # Initialize, train, and load Vanna/Ollama models
├── sql_engine.py          # SQLite connection, query execution, schema introspection
├── text_to_sql.py         # Natural language → SQL translation using Vanna/Ollama
├── ui_app.py              # Streamlit or CLI interface logic
└── utils.py               # Logging, validation, and helper functions

If Streamlit UI exists, place the main entry script (e.g. fedex_app.py) in the root directory, importing from the above modules.

⸻

Steps:
	1.	Identify functional boundaries in vanna_ollama_sqlite_fedex.py.
Example: model training → query generation → SQL execution → UI display.
	2.	Extract and relocate code into respective modules as per the structure above.
	3.	Add persistent model caching:
	•	Save trained Vanna model to a .json or .pkl file inside a /models subfolder.
	•	On startup, check if model exists before retraining.
	•	Allow retraining only if new SQL examples are added.
	4.	Refactor imports so that each component uses relative imports (from .model_manager import load_model).
	5.	Add type hints and docstrings for clarity.
	6.	Add a validation test step at the end to confirm that:
	•	Text-to-SQL translation still works.
	•	Database queries execute correctly.
	•	Streamlit app loads without retraining the model each time.
	7.	Generate a unified entry script (e.g. fedex_main.py) that imports modules and runs the workflow:
	•	Load model
	•	Accept user input
	•	Generate SQL
	•	Execute query
	•	Display results

⸻

Action:
Generate Python files under Vanna/ as described.
Refactor code to ensure modularity, reusability, and performance stability.
Ensure that fedex_main.py runs successfully with identical output to the original script.

⸻

Result:
A clean, modularized Python package where:
	•	Model logic, SQL logic, and UI are separate.
	•	Vanna model is trained only once and reused.
	•	New tools (e.g., MCP-based agents) can import model_manager or sql_engine directly.
	•	Future UI layers (e.g., Streamlit, FastAPI, MCP) can reuse the same backend logic.

⸻

Would you like me to generate the exact module code templates (empty but structured, with proper imports and placeholders) for this folder next?
That will let you drop them into your Cursor project immediately.
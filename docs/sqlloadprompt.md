COSTAR Prompt: Create and Validate SQLite Database from FedEx CSV

Context:
You have successfully downloaded and cleaned shipping rate data from the FedEx Service Guide 2025 into a fedex_rates_final.csv file.
Now you want to:
	1.	Create a SQLite database.
	2.	Upload the CSV data into a structured table.
	3.	Run sample SQL queries to verify data integrity and accuracy.

⸻

Objective:
Generate a Python script that:
	•	Loads the .csv file into a SQLite database named fedex_rates.db.
	•	Creates a table (e.g., fedex_rates) with appropriate data types inferred from the CSV header.
	•	Inserts all rows cleanly, handling nulls and type mismatches.
	•	Runs sample SQL queries to verify data load (e.g., record count, sample rows, unique zones, weight range checks).

⸻

Style:
	•	Use clear, step-by-step code blocks with inline comments.
	•	Follow Python best practices for SQLite (use sqlite3, pandas, and os).
	•	Add exception handling and confirmation print statements for each major step.
	•	Keep file paths relative (so the script runs inside Cursor IDE).

⸻

Task:
Generate a Python script that:
	1.	Imports required libraries (pandas, sqlite3, os).
	2.	Checks if fedex_rates.db already exists and removes it before recreating.
	3.	Reads the CSV file (e.g., fedex_service_guide_2025.csv) into a pandas DataFrame.
	4.	Automatically infers column types.
	5.	Writes the DataFrame into SQLite (to_sql(..., if_exists='replace', index=False)).
	6.	Executes and prints results of these sample SQL queries:
	•	Total record count.
	•	First 5 rows.
	•	Unique zones (SELECT DISTINCT Zone FROM fedex_rates;).
	•	Weight range (SELECT MIN(Weight), MAX(Weight) FROM fedex_rates;).
	•	Example rate check (SELECT * FROM fedex_rates WHERE Zone='2' AND Weight='10';).

⸻

Action:
Write the entire executable script, including:
	•	Environment setup (uv add pandas sqlite3 python-dotenv).
	•	Instructions to load .env if needed for paths.
	•	SQL validation output clearly labeled (e.g., “✅ Data loaded successfully. Record count: 523 rows”).

⸻

Response Format:
Return one complete Python script with:
	•	Step-by-step structure.
	•	Clear print messages for each verification.
	•	No placeholder code.
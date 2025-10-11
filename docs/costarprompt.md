C – Context

You are an expert data extraction agent working on a structured rate table extraction task.
The source document is the FedEx Service Guide 2025 PDF (pages 13–34).
These pages contain U.S. Express Package Rate Tables for Zones 2–8.
Each page follows a consistent format:
•	First column: Weight (lbs) ranging 1–150.
•	Next six columns: numeric rates for FedEx services.
•	Each table header starts with “U.S. Package Rates: Zone [number]”.
•	Ignore gray-shaded header rows, notes, or footnotes below tables.
Each zone is covered in 3 pages. For example zone 2 starts on page 13 and ends in page 15. Zone 3 starts with Page 16-18. Zone 4 starts from page 19-21 and so so forth.
You are helping validate that table extraction works correctly before automated ingestion into a database.
 
O – Objective

Extract the data in clean, tabular format with the following columns:

| Zone | Weight (lbs) | FedEx First Overnight (Next Day by 8 or 8:30 a.m.) | FedEx Priority Overnight (Next Day by 10:30 or 11 a.m.) | FedEx Standard Overnight (Next Day by 5 p.m.) | FedEx 2Day AM (2nd Day by 10:30 or 11 a.m.) | FedEx 2Day (2nd Day by 5 p.m.) | FedEx Express Saver (3rd Day by 5 p.m.) |

Ensure:
•	All values are numeric with two decimals.
•	No symbols, asterisks, or extra spaces.
•	Row order starts at 1 lb and continues sequentially up to 150 lbs.
•	The last row for each zone must end near the 150-lb rate (use that as a sanity check).
•	Include the zone number in each row for cross-validation.
. Validate using good validation data for example in each page from page 13 to page 30. Output must have zones 2 to zone 8. and must have weights all the way to 150 lbs.
Use validation set in validation_set.csv file in the project folder.
 
S – Style

Output as a CSV-style table, not JSON.
Use a clear header row and comma-separated values, so it can be copy-pasted into Excel for visual checking.
Use validation_set_corrected.csv file for visual checking.


...
Do not output markdown fences (no ```csv).
 
T – Tone

Precise and data-focused.
No explanations, summaries, or commentary — just the table.
 
A – Audience

Your output will be immediately copied into Excel by the analyst for verification.
Formatting errors or extra text will break Excel parsing.
Deliver clean, machine-ready tabular data only.
 
R – Response Format
1.	Begin with a single header row.
2.	Each subsequent row must represent one weight (1–150) for a given zone.
3.	Numeric values only; no text or extra lines.
4.	If OCR noise or merged cells are detected, infer the most likely numeric value based on continuity (rates usually increase smoothly by small steps).
5.	Include all available zones (2–8).
6.	End output cleanly without commentary.
7. 
 

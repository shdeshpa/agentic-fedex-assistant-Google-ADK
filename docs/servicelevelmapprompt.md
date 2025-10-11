Create an SQLite script to make a table named fedex_service_tiers with these columns:
	•	id (INTEGER PRIMARY KEY)
	•	service_name (TEXT)
	•	delivery_time_desc (TEXT)
	•	delivery_day (TEXT)
	•	delivery_deadline (TEXT)
Populate this table with the mapping from the following FedEx Express services:
	•	FedEx First Overnight: Next day by 8 or 8:30 a.m.
	•	FedEx Priority Overnight: Next day by 10:30 a.m. or 11 a.m.
	•	FedEx Standard Overnight: Next day by 5 p.m.
	•	FedEx 2Day A.M.: 2nd day by 10:30 a.m. or 11 a.m.
	•	FedEx 2Day: 2nd day by 5 p.m.
	•	FedEx Express Saver: 3rd day by 5 p.m.
Then, write an example SQL query joining this fedex_service_tiers table to a sample shipments table (with columns: shipment_id, service_id, tracking_number) to retrieve the service_name and delivery_time_desc for each shipment.

update sqltester.py to try out new queries by joining this table with other tables with Fedex rates
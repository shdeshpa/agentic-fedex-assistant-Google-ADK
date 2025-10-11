# COSTAR Prompt: VannaAI Trainer for FedEx Rates

## Overview
This document provides comprehensive instructions for training a VannaAI model to accurately translate natural language shipping queries into SQL for a local SQLite database (fedex_rates.db). The database contains shipping rates by Zone, Weight, and ServiceType.

## Setup Requirements
- Local SQLite database: `fedex_rates.db`
- Ollama installed with qwen3 model
- Qdrant vector database (already installed on server)
- Python dependencies: `vanna`, `ollama`, `pandas`, `sqlite-utils`, `python-dotenv`

## Training Objectives
- Connect Vanna to local SQLite database
- Train model using realistic examples of FedEx shipping queries
- Cover both weight/zone and service-tier variations
- Persist learned examples to `fedex_training.json` for reuse
- Support correction-based continuous training

## Database Schema
The database `fedex_rates.db` includes columns:
- `Zone` (INTEGER) - Shipping zones 1-8
- `Weight` (INTEGER) - Package weight in pounds
- `FedEx_First_Overnight` (REAL) - First Overnight service rates
- `FedEx_Priority_Overnight` (REAL) - Priority Overnight service rates
- `FedEx_Standard_Overnight` (REAL) - Standard Overnight service rates
- `FedEx_2Day_AM` (REAL) - 2Day AM service rates
- `FedEx_2Day` (REAL) - 2Day service rates
- `FedEx_Express_Saver` (REAL) - Express Saver service rates

## Comprehensive Training Examples

### Zone-based Queries
```python
# Show all available shipping zones
vn.train(
    question="Show all available FedEx shipping zones",
    sql="SELECT DISTINCT Zone FROM fedex_rates ORDER BY Zone;"
)

# Zone-specific rate queries
vn.train(
    question="What are all the rates for Zone 2?",
    sql="SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2;"
)

vn.train(
    question="Show rates for Zone 3 under 10 lbs",
    sql="SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 3 AND Weight <= 10;"
)
```

### Weight-based Queries
```python
# Weight category queries
vn.train(
    question="List all available weight categories",
    sql="SELECT DISTINCT Weight FROM fedex_rates ORDER BY Weight;"
)

vn.train(
    question="What are the rates for 5 lb packages?",
    sql="SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 5;"
)

vn.train(
    question="Show rates for packages between 10 and 20 lbs",
    sql="SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight BETWEEN 10 AND 20;"
)
```

### Service-tier Comparisons
```python
# Service-specific queries
vn.train(
    question="Compare FedEx 2Day rates across all zones for 10 lbs",
    sql="SELECT Zone, Weight, FedEx_2Day FROM fedex_rates WHERE Weight = 10 ORDER BY Zone;"
)

vn.train(
    question="Show FedEx Priority Overnight rates for Zone 5",
    sql="SELECT Zone, Weight, FedEx_Priority_Overnight FROM fedex_rates WHERE Zone = 5 ORDER BY Weight;"
)

vn.train(
    question="What's the cheapest service for Zone 6, 15 lbs?",
    sql="SELECT Zone, Weight, MIN(FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver) as Cheapest_Rate FROM fedex_rates WHERE Zone = 6 AND Weight = 15;"
)
```

### Rate Analysis Queries
```python
# Rate comparison and analysis
vn.train(
    question="Show average rates by zone for FedEx 2Day service",
    sql="SELECT Zone, AVG(FedEx_2Day) as Avg_Rate FROM fedex_rates GROUP BY Zone ORDER BY Zone;"
)

vn.train(
    question="Find the most expensive rates for each zone",
    sql="SELECT Zone, MAX(FedEx_First_Overnight) as Max_First_Overnight, MAX(FedEx_Priority_Overnight) as Max_Priority_Overnight, MAX(FedEx_Standard_Overnight) as Max_Standard_Overnight, MAX(FedEx_2Day_AM) as Max_2Day_AM, MAX(FedEx_2Day) as Max_2Day, MAX(FedEx_Express_Saver) as Max_Express_Saver FROM fedex_rates GROUP BY Zone;"
)

vn.train(
    question="Show rates between $20 and $40 for Zone 2",
    sql="SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2 AND (FedEx_First_Overnight BETWEEN 20 AND 40 OR FedEx_Priority_Overnight BETWEEN 20 AND 40 OR FedEx_Standard_Overnight BETWEEN 20 AND 40 OR FedEx_2Day_AM BETWEEN 20 AND 40 OR FedEx_2Day BETWEEN 20 AND 40 OR FedEx_Express_Saver BETWEEN 20 AND 40);"
)
```

### Complex Multi-condition Queries
```python
# Multi-condition queries
vn.train(
    question="Show all rates for Zone 4, 25 lbs sorted by service",
    sql="SELECT Zone, Weight, FedEx_First_Overnight as 'First Overnight', FedEx_Priority_Overnight as 'Priority Overnight', FedEx_Standard_Overnight as 'Standard Overnight', FedEx_2Day_AM as '2Day AM', FedEx_2Day as '2Day', FedEx_Express_Saver as 'Express Saver' FROM fedex_rates WHERE Zone = 4 AND Weight = 25;"
)

vn.train(
    question="Find the top 3 cheapest 2Day rates across all zones",
    sql="SELECT Zone, Weight, FedEx_2Day FROM fedex_rates ORDER BY FedEx_2Day ASC LIMIT 3;"
)

vn.train(
    question="Show rate differences between Priority Overnight and 2Day for Zone 7",
    sql="SELECT Zone, Weight, FedEx_Priority_Overnight, FedEx_2Day, (FedEx_Priority_Overnight - FedEx_2Day) as Price_Difference FROM fedex_rates WHERE Zone = 7 ORDER BY Weight;"
)
```

## Complete Training Script

```python
import os
import json
from dotenv import load_dotenv
from vanna.ollama import OllamaVanna
from vanna.qdrant import Qdrant_VectorStore
import sqlite3
import pandas as pd

# 1. Load environment variables
load_dotenv()

# 2. Initialize Vanna with Ollama + Qdrant
class VannaQdrantOllama(Qdrant_VectorStore, OllamaVanna):
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config=config)
        OllamaVanna.__init__(self, config=config)

vn = VannaQdrantOllama(config={
    "model": "qwen2.5:3b",
    "ollama_host": "http://localhost:11434",
    "qdrant_location": "localhost",
    "qdrant_port": 6333,
    "qdrant_collection": "fedex_rates_vanna"
})

# 3. Connect to SQLite database
DB_PATH = "fedex_rates.db"
vn.connect_to_sqlite(DB_PATH)

# 4. Display schema for confirmation
print("📘 Connected to database. Schema:")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(fedex_rates)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")
conn.close()

# 5. Train on schema
print("🔧 Training on database schema...")
tables_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", sqlite3.connect(DB_PATH))

for table_name in tables_df['name']:
    schema_df = pd.read_sql_query(f"PRAGMA table_info({table_name});", sqlite3.connect(DB_PATH))
    columns = []
    for _, row in schema_df.iterrows():
        columns.append(f"{row['name']} {row['type']}")
    ddl = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
    vn.train(ddl=ddl)

# 6. Comprehensive training examples
training_examples = [
    # Zone-based queries
    ("Show all available FedEx shipping zones", "SELECT DISTINCT Zone FROM fedex_rates ORDER BY Zone;"),
    ("What are all the rates for Zone 2?", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2;"),
    ("Show rates for Zone 3 under 10 lbs", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 3 AND Weight <= 10;"),
    
    # Weight-based queries
    ("List all available weight categories", "SELECT DISTINCT Weight FROM fedex_rates ORDER BY Weight;"),
    ("What are the rates for 5 lb packages?", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 5;"),
    ("Show rates for packages between 10 and 20 lbs", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight BETWEEN 10 AND 20;"),
    
    # Service-tier comparisons
    ("Compare FedEx 2Day rates across all zones for 10 lbs", "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates WHERE Weight = 10 ORDER BY Zone;"),
    ("Show FedEx Priority Overnight rates for Zone 5", "SELECT Zone, Weight, FedEx_Priority_Overnight FROM fedex_rates WHERE Zone = 5 ORDER BY Weight;"),
    ("What's the cheapest service for Zone 6, 15 lbs?", "SELECT Zone, Weight, MIN(FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver) as Cheapest_Rate FROM fedex_rates WHERE Zone = 6 AND Weight = 15;"),
    
    # Rate analysis
    ("Show average rates by zone for FedEx 2Day service", "SELECT Zone, AVG(FedEx_2Day) as Avg_Rate FROM fedex_rates GROUP BY Zone ORDER BY Zone;"),
    ("Find the most expensive rates for each zone", "SELECT Zone, MAX(FedEx_First_Overnight) as Max_First_Overnight, MAX(FedEx_Priority_Overnight) as Max_Priority_Overnight, MAX(FedEx_Standard_Overnight) as Max_Standard_Overnight, MAX(FedEx_2Day_AM) as Max_2Day_AM, MAX(FedEx_2Day) as Max_2Day, MAX(FedEx_Express_Saver) as Max_Express_Saver FROM fedex_rates GROUP BY Zone;"),
    ("Show rates between $20 and $40 for Zone 2", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2 AND (FedEx_First_Overnight BETWEEN 20 AND 40 OR FedEx_Priority_Overnight BETWEEN 20 AND 40 OR FedEx_Standard_Overnight BETWEEN 20 AND 40 OR FedEx_2Day_AM BETWEEN 20 AND 40 OR FedEx_2Day BETWEEN 20 AND 40 OR FedEx_Express_Saver BETWEEN 20 AND 40);"),
    
    # Complex queries
    ("Show all rates for Zone 4, 25 lbs", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 4 AND Weight = 25;"),
    ("Find the top 3 cheapest 2Day rates across all zones", "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates ORDER BY FedEx_2Day ASC LIMIT 3;"),
    ("Show rate differences between Priority Overnight and 2Day for Zone 7", "SELECT Zone, Weight, FedEx_Priority_Overnight, FedEx_2Day, (FedEx_Priority_Overnight - FedEx_2Day) as Price_Difference FROM fedex_rates WHERE Zone = 7 ORDER BY Weight;"),
    
    # Additional comprehensive examples
    ("Show all rates for 10 lbs in Zone 2", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2 AND Weight = 10;"),
    ("Compare overnight services for Zone 3", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight FROM fedex_rates WHERE Zone = 3 ORDER BY Weight;"),
    ("What are the FedEx Express Saver rates for all zones at 20 lbs?", "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 20 ORDER BY Zone;"),
    ("Show the cheapest rate for each zone at 15 lbs", "SELECT Zone, Weight, MIN(FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver) as Cheapest_Rate FROM fedex_rates WHERE Weight = 15 GROUP BY Zone ORDER BY Zone;"),
    ("List all rates for Zone 8", "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 8 ORDER BY Weight;")
]

# 7. Train the model on all examples
print("🎓 Training Vanna on comprehensive examples...")
for i, (question, sql) in enumerate(training_examples, 1):
    vn.train(question=question, sql=sql)
    print(f"  ✅ Example {i}/{len(training_examples)}: {question[:50]}...")

print(f"✅ Successfully trained Vanna on {len(training_examples)} examples!")

# 8. Save training data for reuse
training_data = [(q, sql) for q, sql in training_examples]
with open("fedex_training.json", "w") as f:
    json.dump(training_data, f, indent=2)
print("💾 Training data saved to fedex_training.json")

# 9. Function to reload training data
def load_training():
    """Reload training data from JSON file."""
    with open("fedex_training.json", "r") as f:
        data = json.load(f)
        for question, sql in data:
            vn.train(question=question, sql=sql)
    print("🔁 Reloaded training data from fedex_training.json")

# 10. Function to test queries
def test_query(question: str):
    """Test a query and display results."""
    print(f"\n🔍 Testing: {question}")
    try:
        sql = vn.generate_sql(question)
        print(f"🧠 Generated SQL: {sql}")
        
        result = vn.run_sql(sql)
        print("📊 Query Results:")
        print(result.head() if hasattr(result, 'head') else result)
        
    except Exception as e:
        print(f"❌ Error: {e}")

# 11. Interactive testing loop
def interactive_mode():
    """Run interactive query testing."""
    print("\n🚀 Interactive mode started. Type 'exit' to quit.")
    while True:
        question = input("\nAsk your question: ")
        if question.lower() in ['exit', 'quit']:
            break
        test_query(question)

# 12. Example test queries
print("\n🧪 Running example test queries...")
test_queries = [
    "Show all rates for Zone 2",
    "What are the FedEx 2Day rates for 10 lbs?",
    "Compare overnight services for Zone 5",
    "Find the cheapest rate for Zone 3, 15 lbs"
]

for query in test_queries:
    test_query(query)

print("\n✅ Training complete! Use interactive_mode() to test more queries.")
print("📚 Training data saved to fedex_training.json for future use.")
```

## Usage Instructions

1. **Install dependencies:**
   ```bash
   uv add vanna ollama pandas python-dotenv
   ```

2. **Ensure Ollama and Qdrant are running:**
   ```bash
   # Start Ollama
   ollama serve
   
   # Start Qdrant (if using Docker)
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **Run the training script:**
   ```bash
   python vanna_training.py
   ```

4. **Test queries interactively:**
   ```python
   interactive_mode()
   ```

## Key Features

- **Comprehensive Training**: 20+ realistic FedEx shipping queries
- **Schema Awareness**: Automatic database schema training
- **Persistent Training**: Save/load training data as JSON
- **Error Handling**: Robust error handling for malformed SQL
- **Interactive Testing**: Built-in query testing functionality
- **Local Operation**: No external API calls, fully offline

This training setup ensures VannaAI can accurately translate natural language shipping queries into precise SQL statements for the FedEx rates database.


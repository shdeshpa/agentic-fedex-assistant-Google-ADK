# =============================================================================
#  Filename: vanna_ollama_sqlite_fedex.py
#
#  Short Description: Local Text-to-SQL using Vanna + Ollama + Qdrant
#
#  Creation date: 2025-10-08
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Use Vanna.AI with Ollama (qwen3 model) and Qdrant for local text-to-SQL queries.
No cloud calls, fully local LLM and vector store.
"""

import sqlite3
from pathlib import Path

import pandas as pd
from loguru import logger
from vanna.ollama import Ollama
from vanna.qdrant import Qdrant_VectorStore


class VannaQdrantOllama(Qdrant_VectorStore, Ollama):
    """
    Custom Vanna class combining Qdrant vector store with Ollama LLM.
    This provides both embedding storage and local LLM inference.
    """
    def __init__(self, config: dict = None):
        """Initialize with Qdrant and Ollama configurations."""
        Qdrant_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


class VannaFedExRates:
    """Local text-to-SQL interface for FedEx rates using Vanna + Ollama + Qdrant."""

    def __init__(
        self, 
        db_path: Path, 
        model: str = "qwen2.5:3b",
        ollama_host: str = "http://localhost:11434",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333
    ) -> None:
        """
        Initialize Vanna with Qdrant + Ollama backend.
        
        Args:
            db_path: Path to SQLite database
            model: Ollama model name (qwen2.5:3b, llama3, mistral, etc.)
            ollama_host: Ollama server URL
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
        """
        self.db_path = db_path
        self.model = model
        self.ollama_host = ollama_host
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.conn = None
        self.vn = None
        
        logger.info(f"Initializing Vanna with Ollama model: {model}")
        logger.info(f"Using Qdrant at {qdrant_host}:{qdrant_port}")
        
    def connect_database(self) -> None:
        """Connect to SQLite database."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            logger.success(f"✅ Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise
            
    def initialize_vanna(self) -> None:
        """Initialize Vanna with Qdrant + Ollama backend."""
        try:
            logger.info(f"Connecting to Ollama at {self.ollama_host}")
            logger.info(f"Connecting to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
            
            # Initialize Vanna with both Qdrant and Ollama
            self.vn = VannaQdrantOllama(
                config={
                    "model": self.model,
                    "ollama_host": self.ollama_host,
                    "qdrant_location": self.qdrant_host,
                    "qdrant_port": self.qdrant_port,
                    "qdrant_collection": "fedex_rates_collection"
                }
            )
            
            # Connect Vanna to SQLite
            self.vn.connect_to_sqlite(str(self.db_path))
            
            logger.success("✅ Vanna initialized with Qdrant + Ollama backend")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vanna: {e}")
            logger.info("\nTroubleshooting:")
            logger.info("1. Make sure Ollama is running: ollama serve")
            logger.info("2. Make sure Qdrant is running on port 6333")
            logger.info(f"3. Check model is available: ollama list")
            raise
    
    def train_on_schema(self) -> None:
        """Train Vanna on database schema."""
        logger.info("\n📚 Training Vanna on database schema...")
        
        try:
            # Get all tables
            tables_df = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table';", 
                self.conn
            )
            
            logger.info(f"Found {len(tables_df)} table(s)")
            
            for table_name in tables_df['name']:
                logger.info(f"  Loading schema for table: {table_name}")
                
                # Get table schema
                schema_df = pd.read_sql_query(
                    f"PRAGMA table_info({table_name});", 
                    self.conn
                )
                
                # Create DDL statement
                columns = []
                for _, row in schema_df.iterrows():
                    col_def = f"{row['name']} {row['type']}"
                    columns.append(col_def)
                
                ddl = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
                
                # Train on schema
                self.vn.train(ddl=ddl)
                logger.info(f"    ✓ Schema loaded for {table_name}")
            
            # Add documentation for table relationships
            documentation = """
            Database Documentation:
            
            fedex_rates table:
            - Contains shipping rates for all zones (2-8) and weights (1-150 lbs)
            - 6 service columns: FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, 
              FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver
            - Zone: INTEGER (2-8)
            - Weight: INTEGER (1-150 lbs)
            - Each service column: REAL (rate in dollars)
            
            Key relationships:
            - Zone determines shipping distance (higher zone = farther distance)
            - Weight affects rate (heavier packages cost more)
            - Services have different delivery speeds and costs
            - First_Overnight = fastest, most expensive
            - Express_Saver = slowest, cheapest
            """
            self.vn.train(documentation=documentation)
            logger.info("  ✓ Table relationship documentation added")
            
            logger.success("✅ Schema training complete")
            
        except Exception as e:
            logger.error(f"❌ Schema training failed: {e}")
            raise
    
    def train_on_examples(self) -> None:
        """Train Vanna with comprehensive examples from vanna.md documentation."""
        logger.info("\n📝 Training Vanna with comprehensive example queries...")
        
        examples = [
            # Zone-based queries
            {
                "question": "Show all available FedEx shipping zones",
                "sql": "SELECT DISTINCT Zone FROM fedex_rates ORDER BY Zone;"
            },
            {
                "question": "What are all the rates for Zone 2?",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2;"
            },
            {
                "question": "Show rates for Zone 3 under 10 lbs",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 3 AND Weight <= 10;"
            },
            {
                "question": "Show all rates for Zone 4",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 4 ORDER BY Weight;"
            },
            {
                "question": "List all rates for Zone 8",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 8 ORDER BY Weight;"
            },
            
            # Weight-based queries
            {
                "question": "List all available weight categories",
                "sql": "SELECT DISTINCT Weight FROM fedex_rates ORDER BY Weight;"
            },
            {
                "question": "What are the rates for 5 lb packages?",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 5;"
            },
            {
                "question": "Show rates for packages between 10 and 20 lbs",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight BETWEEN 10 AND 20;"
            },
            {
                "question": "What are the rates for 10 lb packages?",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 10 ORDER BY Zone;"
            },
            {
                "question": "Show all rates for 25 lbs",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 25 ORDER BY Zone;"
            },
            
            # Service-tier comparisons
            {
                "question": "Compare FedEx 2Day rates across all zones for 10 lbs",
                "sql": "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates WHERE Weight = 10 ORDER BY Zone;"
            },
            {
                "question": "Show FedEx Priority Overnight rates for Zone 5",
                "sql": "SELECT Zone, Weight, FedEx_Priority_Overnight FROM fedex_rates WHERE Zone = 5 ORDER BY Weight;"
            },
            {
                "question": "What's the cheapest service for Zone 6, 15 lbs?",
                "sql": "SELECT Zone, Weight, MIN(FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver) as Cheapest_Rate FROM fedex_rates WHERE Zone = 6 AND Weight = 15;"
            },
            {
                "question": "Show FedEx Express Saver rates for all zones at 20 lbs",
                "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 20 ORDER BY Zone;"
            },
            {
                "question": "Compare overnight services for Zone 3",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight FROM fedex_rates WHERE Zone = 3 ORDER BY Weight;"
            },
            
            # Rate analysis queries
            {
                "question": "Show average rates by zone for FedEx 2Day service",
                "sql": "SELECT Zone, AVG(FedEx_2Day) as Avg_Rate FROM fedex_rates GROUP BY Zone ORDER BY Zone;"
            },
            {
                "question": "Find the most expensive rates for each zone",
                "sql": "SELECT Zone, MAX(FedEx_First_Overnight) as Max_First_Overnight, MAX(FedEx_Priority_Overnight) as Max_Priority_Overnight, MAX(FedEx_Standard_Overnight) as Max_Standard_Overnight, MAX(FedEx_2Day_AM) as Max_2Day_AM, MAX(FedEx_2Day) as Max_2Day, MAX(FedEx_Express_Saver) as Max_Express_Saver FROM fedex_rates GROUP BY Zone;"
            },
            {
                "question": "Show rates between $20 and $40 for Zone 2",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2 AND (FedEx_First_Overnight BETWEEN 20 AND 40 OR FedEx_Priority_Overnight BETWEEN 20 AND 40 OR FedEx_Standard_Overnight BETWEEN 20 AND 40 OR FedEx_2Day_AM BETWEEN 20 AND 40 OR FedEx_2Day BETWEEN 20 AND 40 OR FedEx_Express_Saver BETWEEN 20 AND 40);"
            },
            {
                "question": "What are the average rates for each zone?",
                "sql": "SELECT Zone, ROUND(AVG(FedEx_2Day), 2) as avg_2day_rate, ROUND(AVG(FedEx_Express_Saver), 2) as avg_express_saver FROM fedex_rates GROUP BY Zone ORDER BY Zone;"
            },
            {
                "question": "Show the cheapest rate for each zone at 15 lbs",
                "sql": "SELECT Zone, Weight, MIN(FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver) as Cheapest_Rate FROM fedex_rates WHERE Weight = 15 GROUP BY Zone ORDER BY Zone;"
            },
            
            # Complex multi-condition queries
            {
                "question": "Show all rates for Zone 4, 25 lbs",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight as 'First Overnight', FedEx_Priority_Overnight as 'Priority Overnight', FedEx_Standard_Overnight as 'Standard Overnight', FedEx_2Day_AM as '2Day AM', FedEx_2Day as '2Day', FedEx_Express_Saver as 'Express Saver' FROM fedex_rates WHERE Zone = 4 AND Weight = 25;"
            },
            {
                "question": "Find the top 3 cheapest 2Day rates across all zones",
                "sql": "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates ORDER BY FedEx_2Day ASC LIMIT 3;"
            },
            {
                "question": "Show rate differences between Priority Overnight and 2Day for Zone 7",
                "sql": "SELECT Zone, Weight, FedEx_Priority_Overnight, FedEx_2Day, (FedEx_Priority_Overnight - FedEx_2Day) as Price_Difference FROM fedex_rates WHERE Zone = 7 ORDER BY Weight;"
            },
            {
                "question": "Compare all service rates for Zone 5, 50 lbs",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 5 AND Weight = 50;"
            },
            {
                "question": "Show all rates for 10 lbs in Zone 2",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2 AND Weight = 10;"
            },
            
            # Additional comprehensive examples
            {
                "question": "How many total records are in the database?",
                "sql": "SELECT COUNT(*) as total_records FROM fedex_rates;"
            },
            {
                "question": "Show me the first 5 records",
                "sql": "SELECT * FROM fedex_rates LIMIT 5;"
            },
            {
                "question": "What's the FedEx 2Day rate for a 10 lb package in Zone 2?",
                "sql": "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates WHERE Zone = 2 AND Weight = 10;"
            },
            {
                "question": "Find the cheapest Express Saver rate for Zone 3",
                "sql": "SELECT MIN(FedEx_Express_Saver) as cheapest_rate FROM fedex_rates WHERE Zone = 3;"
            },
            {
                "question": "How many weight options are available per zone?",
                "sql": "SELECT Zone, COUNT(DISTINCT Weight) as weight_options FROM fedex_rates GROUP BY Zone;"
            },
            {
                "question": "What's the most expensive rate in the entire database?",
                "sql": "SELECT Zone, Weight, FedEx_First_Overnight as highest_rate FROM fedex_rates ORDER BY FedEx_First_Overnight DESC LIMIT 1;"
            },
            {
                "question": "Show rates for all zones at 25 pounds",
                "sql": "SELECT Zone, Weight, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 25 ORDER BY Zone;"
            },
            {
                "question": "FedEx Priority Overnight rates for Zone 2",
                "sql": "SELECT FedEx_Priority_Overnight FROM fedex_rates WHERE Zone = 2 ORDER BY Weight;"
            },
            {
                "question": "What is the cheapest rate for Zone 3?",
                "sql": "SELECT MIN(FedEx_Express_Saver) FROM fedex_rates WHERE Zone = 3;"
            },
            {
                "question": "What is rate for 4 lbs package to zone 6 that delivers next day 9 am?",
                "sql": "SELECT FedEx_First_Overnight FROM fedex_rates WHERE Zone = 6 AND Weight = 4 AND FedEx_First_Overnight IS NOT NULL;"
            },
        ]
        
        for idx, example in enumerate(examples, 1):
            try:
                self.vn.train(
                    question=example["question"],
                    sql=example["sql"]
                )
                logger.info(f"  ✓ Example {idx}/{len(examples)}: {example['question'][:60]}...")
            except Exception as e:
                logger.warning(f"  ⚠ Failed to train example {idx}: {e}")
        
        logger.success(f"✅ Trained on {len(examples)} comprehensive example queries")
        
        # Save training data for reuse
        self._save_training_data(examples)
    
    def _save_training_data(self, examples: list) -> None:
        """Save training examples to JSON file for reuse."""
        try:
            import json
            training_data = [(ex["question"], ex["sql"]) for ex in examples]
            
            # Save to project root
            project_root = Path(__file__).parent.parent
            training_file = project_root / "fedex_training.json"
            
            with open(training_file, "w") as f:
                json.dump(training_data, f, indent=2)
            
            logger.info(f"💾 Training data saved to {training_file}")
        except Exception as e:
            logger.warning(f"⚠ Failed to save training data: {e}")
    
    def load_training_data(self) -> None:
        """Load training data from JSON file."""
        try:
            import json
            project_root = Path(__file__).parent.parent
            training_file = project_root / "fedex_training.json"
            
            if not training_file.exists():
                logger.warning("⚠ Training data file not found, skipping load")
                return
            
            with open(training_file, "r") as f:
                training_data = json.load(f)
            
            logger.info(f"📂 Loading {len(training_data)} training examples from file...")
            
            for question, sql in training_data:
                self.vn.train(question=question, sql=sql)
            
            logger.success(f"✅ Loaded {len(training_data)} training examples from file")
        except Exception as e:
            logger.warning(f"⚠ Failed to load training data: {e}")
    
    def query(self, question: str) -> pd.DataFrame | None:
        """
        Generate SQL from natural language and execute query.
        
        Args:
            question: Natural language question
            
        Returns:
            DataFrame with results or None if error
        """
        try:
            logger.info(f"\n💭 Question: {question}")
            
            # Generate SQL
            sql = self.vn.generate_sql(question)
            logger.info(f"🧠 Generated SQL:\n{sql}")
            
            # Execute query
            df = pd.read_sql_query(sql, self.conn)
            
            logger.success("✅ Query executed successfully")
            return df
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return None
    
    def interactive_loop(self) -> None:
        """Run interactive text-to-SQL loop."""
        logger.info("\n" + "="*70)
        logger.info("🚀 VANNA INTERACTIVE TEXT-TO-SQL")
        logger.info("="*70)
        logger.info("Ask questions in natural language about FedEx shipping rates")
        logger.info("Type 'exit' or 'quit' to end the session")
        logger.info("Type 'help' for example questions")
        logger.info("="*70 + "\n")
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    logger.info("👋 Ending session...")
                    break
                
                if question.lower() == 'help':
                    self._show_help()
                    continue
                
                if not question:
                    continue
                
                # Execute query
                df = self.query(question)
                
                if df is not None:
                    print("\n📦 Results:")
                    print(df.to_string(index=False))
                    print(f"\nRows returned: {len(df)}")
                    
            except KeyboardInterrupt:
                logger.info("\n👋 Session interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
    
    def _show_help(self) -> None:
        """Display comprehensive example questions from vanna.md training."""
        print("\n📚 Comprehensive Example Questions:")
        print("\n  Zone-based Queries:")
        print("    • Show all available FedEx shipping zones")
        print("    • What are all the rates for Zone 2?")
        print("    • Show rates for Zone 3 under 10 lbs")
        print("    • Show all rates for Zone 4")
        print("    • List all rates for Zone 8")
        print("\n  Weight-based Queries:")
        print("    • List all available weight categories")
        print("    • What are the rates for 5 lb packages?")
        print("    • Show rates for packages between 10 and 20 lbs")
        print("    • What are the rates for 10 lb packages?")
        print("    • Show all rates for 25 lbs")
        print("\n  Service-tier Comparisons:")
        print("    • Compare FedEx 2Day rates across all zones for 10 lbs")
        print("    • Show FedEx Priority Overnight rates for Zone 5")
        print("    • What's the cheapest service for Zone 6, 15 lbs?")
        print("    • Show FedEx Express Saver rates for all zones at 20 lbs")
        print("    • Compare overnight services for Zone 3")
        print("\n  Rate Analysis:")
        print("    • Show average rates by zone for FedEx 2Day service")
        print("    • Find the most expensive rates for each zone")
        print("    • Show rates between $20 and $40 for Zone 2")
        print("    • What are the average rates for each zone?")
        print("    • Show the cheapest rate for each zone at 15 lbs")
        print("\n  Complex Multi-condition:")
        print("    • Show all rates for Zone 4, 25 lbs")
        print("    • Find the top 3 cheapest 2Day rates across all zones")
        print("    • Show rate differences between Priority Overnight and 2Day for Zone 7")
        print("    • Compare all service rates for Zone 5, 50 lbs")
        print("    • Show all rates for 10 lbs in Zone 2")
        print("\n  Additional Examples:")
        print("    • How many total records are in the database?")
        print("    • Show me the first 5 records")
        print("    • What's the FedEx 2Day rate for a 10 lb package in Zone 2?")
        print("    • Find the cheapest Express Saver rate for Zone 3")
        print("    • What's the most expensive rate in the entire database?")
    
    def test_query(self, question: str) -> None:
        """Test a query and display results."""
        logger.info(f"\n🔍 Testing: {question}")
        try:
            sql = self.vn.generate_sql(question)
            logger.info(f"🧠 Generated SQL: {sql}")
            
            result = self.query(question)
            if result is not None:
                logger.info("📊 Query Results:")
                print(result.to_string(index=False))
            else:
                logger.error("❌ Query failed")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
    
    def run_example_tests(self) -> None:
        """Run example test queries to validate training."""
        logger.info("\n🧪 Running example test queries...")
        
        test_queries = [
            "Show all rates for Zone 2",
            "What are the FedEx 2Day rates for 10 lbs?",
            "Compare overnight services for Zone 5",
            "Find the cheapest rate for Zone 3, 15 lbs"
        ]
        
        for query in test_queries:
            self.test_query(query)
            print()  # Add spacing between tests
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.success("✅ Database connection closed")


def main() -> None:
    """Main execution workflow."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    db_path = project_root / "fedex_rates.db"
    
    # Check database exists
    if not db_path.exists():
        logger.error(f"❌ Database not found: {db_path}")
        logger.error("Please run load_to_sqlite.py first")
        return
    
    logger.info("\n" + "="*70)
    logger.info("🚀 VANNA + OLLAMA + QDRANT LOCAL TEXT-TO-SQL")
    logger.info("="*70 + "\n")
    
    try:
        # Initialize Vanna
        vanna = VannaFedExRates(
            db_path=db_path,
            model="qwen2.5:3b",  # Using qwen3 as requested
            ollama_host="http://localhost:11434",
            qdrant_host="localhost",
            qdrant_port=6333
        )
        
        # Step 1: Connect to database
        logger.info("STEP 1: Connecting to SQLite database")
        vanna.connect_database()
        print()
        
        # Step 2: Initialize Vanna
        logger.info("STEP 2: Initializing Vanna with Qdrant + Ollama")
        vanna.initialize_vanna()
        print()
        
        # Step 3: Train on schema
        logger.info("STEP 3: Training on database schema")
        vanna.train_on_schema()
        print()
        
        # Step 4: Train on examples (or load existing)
        logger.info("STEP 4: Training on example queries")
        project_root = Path(__file__).parent.parent
        training_file = project_root / "fedex_training.json"
        
        if training_file.exists():
            logger.info("📂 Found existing training data, loading from file...")
            vanna.load_training_data()
        else:
            logger.info("📝 No existing training data found, creating comprehensive examples...")
            vanna.train_on_examples()
        print()
        
        # Step 5: Run example tests
        logger.info("STEP 5: Running example tests to validate training")
        vanna.run_example_tests()
        print()
        
        # Step 6: Interactive loop
        logger.info("STEP 6: Starting interactive session")
        vanna.interactive_loop()
        
        # Cleanup
        vanna.close()
        
        logger.info("\n" + "="*70)
        logger.success("✅ SESSION ENDED")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Make sure Ollama is running: ollama serve")
        logger.info("2. Check model is available: ollama pull qwen2.5:3b")
        logger.info("3. Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
        raise


if __name__ == "__main__":
    main()

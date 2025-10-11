# =============================================================================
#  Filename: text_to_sql.py
#
#  Short Description: Natural language to SQL translation engine
#
#  Creation date: 2025-10-09
#  Author:  Shrinivas Deshpande
# =============================================================================

"""
Text-to-SQL Engine for Vanna FedEx Rate Query System.

Handles natural language to SQL translation using VannaAI + Ollama.
Extracted from the original vanna_ollama_sqlite_fedex.py file.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from loguru import logger

from .config import VannaConfig
from .model_manager import VannaModelManager
from .sql_engine import SQLiteEngine


class TextToSQLEngine:
    """
    Text-to-SQL translation engine using VannaAI + Ollama.
    
    This class handles:
    - Natural language query processing
    - SQL generation using trained Vanna model
    - Query execution with error handling
    - Result formatting and validation
    """
    
    def __init__(self, config: VannaConfig):
        """
        Initialize the text-to-SQL engine.
        
        Args:
            config: VannaConfig instance
        """
        self.config = config
        self.model_manager: Optional[VannaModelManager] = None
        self.sql_engine: Optional[SQLiteEngine] = None
        
        logger.info("Initializing TextToSQLEngine")
    
    def initialize(self) -> None:
        """Initialize the text-to-SQL engine with model manager and SQL engine."""
        try:
            # Initialize model manager
            logger.info("Initializing model manager...")
            self.model_manager = VannaModelManager(self.config)
            self.model_manager.connect_database()
            self.model_manager.initialize_vanna()
            self.model_manager.train_on_schema()
            self.model_manager.ensure_trained()
            
            # Initialize SQL engine
            logger.info("Initializing SQL engine...")
            self.sql_engine = SQLiteEngine(self.config)
            self.sql_engine.connect()
            
            logger.success("✅ TextToSQLEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize TextToSQLEngine: {e}")
            raise
    
    def query(self, question: str) -> Optional[pd.DataFrame]:
        """
        Process a natural language question and return results.
        
        This is the main method that replicates the query() method from
        the original VannaFedExRates class.
        
        Args:
            question: Natural language question
            
        Returns:
            DataFrame with results or None if error
        """
        if not self.model_manager or not self.sql_engine:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        
        try:
            logger.info(f"\n💭 Question: {question}")
            
            # Generate SQL using Vanna
            vanna = self.model_manager.get_vanna_instance()
            sql = vanna.generate_sql(question)
            logger.info(f"🧠 Generated SQL:\n{sql}")
            
            # Execute query using SQL engine
            df = self.sql_engine.execute_query(sql)
            
            logger.success("✅ Query executed successfully")
            return df
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return None
    
    def generate_sql(self, question: str) -> Optional[str]:
        """
        Generate SQL from natural language question.
        
        Args:
            question: Natural language question
            
        Returns:
            Generated SQL query or None if error
        """
        if not self.model_manager:
            raise RuntimeError("Model manager not initialized. Call initialize() first.")
        
        try:
            vanna = self.model_manager.get_vanna_instance()
            sql = vanna.generate_sql(question)
            logger.info(f"🧠 Generated SQL: {sql}")
            return sql
            
        except Exception as e:
            logger.error(f"❌ SQL generation failed: {e}")
            return None
    
    def execute_sql(self, sql: str) -> Optional[pd.DataFrame]:
        """
        Execute a SQL query directly.
        
        Args:
            sql: SQL query string
            
        Returns:
            DataFrame with results or None if error
        """
        if not self.sql_engine:
            raise RuntimeError("SQL engine not initialized. Call initialize() first.")
        
        try:
            df = self.sql_engine.execute_query(sql)
            logger.success("✅ SQL executed successfully")
            return df
            
        except Exception as e:
            logger.error(f"❌ SQL execution failed: {e}")
            return None
    
    def query_with_sql(self, question: str) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
        """
        Process a natural language question and return results with SQL.
        
        Args:
            question: Natural language question
            
        Returns:
            Tuple of (DataFrame or None, SQL or None, error message or None)
        """
        if not self.model_manager or not self.sql_engine:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        
        try:
            logger.info(f"\n💭 Question: {question}")
            
            # Generate SQL using Vanna
            vanna = self.model_manager.get_vanna_instance()
            sql = vanna.generate_sql(question)
            logger.info(f"🧠 Generated SQL:\n{sql}")
            
            # Execute query using SQL engine
            df = self.sql_engine.execute_query(sql)
            
            logger.success("✅ Query executed successfully")
            return df, sql, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Query failed: {error_msg}")
            return None, None, error_msg
    
    def test_query(self, question: str) -> None:
        """
        Test a query and display results.
        
        This replicates the test_query() method from the original file.
        
        Args:
            question: Natural language question to test
        """
        logger.info(f"\n🔍 Testing: {question}")
        
        try:
            # Generate SQL
            sql = self.generate_sql(question)
            if not sql:
                logger.error("❌ Failed to generate SQL")
                return
            
            # Execute query
            result = self.query(question)
            if result is not None:
                logger.info("📊 Query Results:")
                print(result.to_string(index=False))
            else:
                logger.error("❌ Query failed")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
    
    def run_example_tests(self) -> None:
        """
        Run example test queries to validate training.
        
        This replicates the run_example_tests() method from the original file.
        """
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
    
    def get_model_manager(self) -> VannaModelManager:
        """
        Get the model manager instance.
        
        Returns:
            VannaModelManager instance
        """
        if not self.model_manager:
            raise RuntimeError("Model manager not initialized")
        return self.model_manager
    
    def get_sql_engine(self) -> SQLiteEngine:
        """
        Get the SQL engine instance.
        
        Returns:
            SQLiteEngine instance
        """
        if not self.sql_engine:
            raise RuntimeError("SQL engine not initialized")
        return self.sql_engine
    
    def close(self) -> None:
        """Close connections and cleanup resources."""
        if self.model_manager:
            self.model_manager.close()
        if self.sql_engine:
            self.sql_engine.disconnect()
        logger.success("✅ TextToSQLEngine closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_text_to_sql_engine(config: VannaConfig) -> TextToSQLEngine:
    """
    Factory function to create and initialize a text-to-SQL engine.
    
    Args:
        config: VannaConfig instance
        
    Returns:
        Initialized TextToSQLEngine instance
    """
    engine = TextToSQLEngine(config)
    engine.initialize()
    return engine


class QueryHandler:
    """
    High-level query handler that provides a simple interface for processing queries.
    
    This class provides the same interface as the original VannaFedExRates.query() method
    but uses the modular components internally.
    """
    
    def __init__(self, text_to_sql_engine: TextToSQLEngine):
        """
        Initialize the query handler.
        
        Args:
            text_to_sql_engine: TextToSQLEngine instance
        """
        self.engine = text_to_sql_engine
    
    def query(self, question: str) -> Optional[pd.DataFrame]:
        """
        Process a natural language question and return results.
        
        Args:
            question: Natural language question
            
        Returns:
            DataFrame with results or None if error
        """
        return self.engine.query(question)
    
    def query_with_sql(self, question: str) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
        """
        Process a natural language question and return results with SQL.
        
        Args:
            question: Natural language question
            
        Returns:
            Tuple of (DataFrame or None, SQL or None, error message or None)
        """
        return self.engine.query_with_sql(question)


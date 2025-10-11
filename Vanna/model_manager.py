# =============================================================================
#  Filename: model_manager.py
#
#  Short Description: Vanna model initialization, training, and persistence
#
#  Creation date: 2025-10-09
#  Author:  Shrinivas Deshpande
# =============================================================================

"""
Model Manager for Vanna FedEx Rate Query System.

Handles Vanna model initialization, training, persistence, and caching.
Extracted from the original vanna_ollama_sqlite_fedex.py file.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from loguru import logger

from vanna.ollama import Ollama
from vanna.qdrant import Qdrant_VectorStore

from .config import VannaConfig, TRAINING_EXAMPLES, DATABASE_DOCUMENTATION


class VannaQdrantOllama(Qdrant_VectorStore, Ollama):
    """
    Custom Vanna class combining Qdrant vector store with Ollama LLM.
    This provides both embedding storage and local LLM inference.
    Extracted from original vanna_ollama_sqlite_fedex.py.
    """
    
    def __init__(self, config: VannaConfig):
        """Initialize with Qdrant and Ollama configurations."""
        self.config = config
        
        # Initialize Qdrant with configuration
        qdrant_config = {
            "qdrant_location": config.qdrant_host,
            "qdrant_port": config.qdrant_port,
            "qdrant_collection": config.qdrant_collection
        }
        Qdrant_VectorStore.__init__(self, config=qdrant_config)
        
        # Initialize Ollama with configuration
        ollama_config = {
            "model": config.model,
            "ollama_host": config.ollama_host
        }
        Ollama.__init__(self, config=ollama_config)


class VannaModelManager:
    """
    Manages Vanna model initialization, training, and persistence.
    
    This class handles:
    - Model initialization with Qdrant + Ollama
    - Database schema training
    - Training example loading and persistence
    - Model caching to avoid retraining
    """
    
    def __init__(self, config: VannaConfig):
        """
        Initialize the model manager.
        
        Args:
            config: VannaConfig instance with all configuration settings
        """
        self.config = config
        self.vanna: Optional[VannaQdrantOllama] = None
        self.db_conn: Optional[sqlite3.Connection] = None
        
        logger.info(f"Initializing VannaModelManager with model: {config.model}")
        logger.info(f"Using Qdrant at {config.qdrant_host}:{config.qdrant_port}")
    
    def connect_database(self) -> None:
        """Connect to SQLite database."""
        try:
            self.db_conn = sqlite3.connect(str(self.config.db_path))
            logger.success(f"✅ Connected to database: {self.config.db_path}")
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise
    
    def initialize_vanna(self) -> None:
        """Initialize Vanna with Qdrant + Ollama backend."""
        try:
            logger.info(f"Connecting to Ollama at {self.config.ollama_host}")
            logger.info(f"Connecting to Qdrant at {self.config.qdrant_host}:{self.config.qdrant_port}")
            
            # Initialize Vanna with both Qdrant and Ollama
            self.vanna = VannaQdrantOllama(self.config)
            
            # Connect Vanna to SQLite
            self.vanna.connect_to_sqlite(str(self.config.db_path))
            
            logger.success("✅ Vanna initialized with Qdrant + Ollama backend")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vanna: {e}")
            logger.info("\nTroubleshooting:")
            logger.info("1. Make sure Ollama is running: ollama serve")
            logger.info("2. Make sure Qdrant is running on port 6333")
            logger.info(f"3. Check model is available: ollama list")
            raise
    
    def is_model_trained(self) -> bool:
        """
        Check if the model has been trained by looking for training data file.
        
        Returns:
            True if training data exists, False otherwise
        """
        return self.config.training_data_file.exists()
    
    def train_on_schema(self) -> None:
        """Train Vanna on database schema."""
        if not self.vanna:
            raise RuntimeError("Vanna not initialized. Call initialize_vanna() first.")
        
        if not self.db_conn:
            raise RuntimeError("Database not connected. Call connect_database() first.")
        
        logger.info("\n📚 Training Vanna on database schema...")
        
        try:
            # Get all tables
            tables_df = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table';", 
                self.db_conn
            )
            
            logger.info(f"Found {len(tables_df)} table(s)")
            
            for table_name in tables_df['name']:
                logger.info(f"  Loading schema for table: {table_name}")
                
                # Get table schema
                schema_df = pd.read_sql_query(
                    f"PRAGMA table_info({table_name});", 
                    self.db_conn
                )
                
                # Create DDL statement
                columns = []
                for _, row in schema_df.iterrows():
                    col_def = f"{row['name']} {row['type']}"
                    columns.append(col_def)
                
                ddl = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
                
                # Train on schema
                self.vanna.train(ddl=ddl)
                logger.info(f"    ✓ Schema loaded for {table_name}")
            
            # Add documentation for table relationships
            self.vanna.train(documentation=DATABASE_DOCUMENTATION)
            logger.info("  ✓ Table relationship documentation added")
            
            logger.success("✅ Schema training complete")
            
        except Exception as e:
            logger.error(f"❌ Schema training failed: {e}")
            raise
    
    def train_on_examples(self) -> None:
        """Train Vanna with comprehensive examples from config."""
        if not self.vanna:
            raise RuntimeError("Vanna not initialized. Call initialize_vanna() first.")
        
        logger.info("\n📝 Training Vanna with comprehensive example queries...")
        
        for idx, example in enumerate(TRAINING_EXAMPLES, 1):
            try:
                self.vanna.train(
                    question=example["question"],
                    sql=example["sql"]
                )
                logger.info(f"  ✓ Example {idx}/{len(TRAINING_EXAMPLES)}: {example['question'][:60]}...")
            except Exception as e:
                logger.warning(f"  ⚠ Failed to train example {idx}: {e}")
        
        logger.success(f"✅ Trained on {len(TRAINING_EXAMPLES)} comprehensive example queries")
        
        # Save training data for reuse
        self._save_training_data()
    
    def load_training_data(self) -> None:
        """Load training data from JSON file."""
        if not self.vanna:
            raise RuntimeError("Vanna not initialized. Call initialize_vanna() first.")
        
        try:
            if not self.config.training_data_file.exists():
                logger.warning("⚠ Training data file not found, skipping load")
                return
            
            with open(self.config.training_data_file, "r") as f:
                training_data: List[Tuple[str, str]] = json.load(f)
            
            logger.info(f"📂 Loading {len(training_data)} training examples from file...")
            
            for question, sql in training_data:
                self.vanna.train(question=question, sql=sql)
            
            logger.success(f"✅ Loaded {len(training_data)} training examples from file")
        except Exception as e:
            logger.warning(f"⚠ Failed to load training data: {e}")
    
    def _save_training_data(self) -> None:
        """Save training examples to JSON file for reuse."""
        try:
            training_data = [(ex["question"], ex["sql"]) for ex in TRAINING_EXAMPLES]
            
            with open(self.config.training_data_file, "w") as f:
                json.dump(training_data, f, indent=2)
            
            logger.info(f"💾 Training data saved to {self.config.training_data_file}")
        except Exception as e:
            logger.warning(f"⚠ Failed to save training data: {e}")
    
    def get_vanna_instance(self) -> VannaQdrantOllama:
        """
        Get the initialized Vanna instance.
        
        Returns:
            VannaQdrantOllama instance
            
        Raises:
            RuntimeError: If Vanna is not initialized
        """
        if not self.vanna:
            raise RuntimeError("Vanna not initialized. Call initialize_vanna() first.")
        return self.vanna
    
    def ensure_trained(self) -> None:
        """
        Ensure the model is trained, either by loading existing training or training from scratch.
        """
        if self.is_model_trained():
            logger.info("📂 Found existing training data, loading from file...")
            self.load_training_data()
        else:
            logger.info("📝 No existing training data found, creating comprehensive examples...")
            self.train_on_examples()
    
    def close(self) -> None:
        """Close database connection."""
        if self.db_conn:
            self.db_conn.close()
            logger.success("✅ Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_model_manager(config: VannaConfig) -> VannaModelManager:
    """
    Factory function to create and initialize a model manager.
    
    Args:
        config: VannaConfig instance
        
    Returns:
        Initialized VannaModelManager instance
    """
    manager = VannaModelManager(config)
    manager.connect_database()
    manager.initialize_vanna()
    manager.train_on_schema()
    manager.ensure_trained()
    
    return manager


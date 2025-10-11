# =============================================================================
#  Filename: __init__.py
#
#  Short Description: Vanna package initialization for modular FedEx rate queries
#
#  Creation date: 2025-10-09
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Vanna Package - Modular FedEx Rate Query System

This package provides a modular, maintainable structure for text-to-SQL
querying of FedEx shipping rates using VannaAI + Ollama + Qdrant.

Modules:
- config: Configuration and constants
- model_manager: Vanna model initialization and training
- sql_engine: SQLite operations and schema introspection
- text_to_sql: Natural language to SQL translation
- utils: Logging, validation, and helper functions

Note: Streamlit UI is now handled by fedex_langgraph_app.py
"""

from .config import VannaConfig
from .model_manager import VannaModelManager
from .sql_engine import SQLiteEngine
from .text_to_sql import TextToSQLEngine
from .utils import setup_logging, validate_database

__version__ = "1.0.0"
__author__ = "Asif Qamar"

__all__ = [
    "VannaConfig",
    "VannaModelManager", 
    "SQLiteEngine",
    "TextToSQLEngine",
    "setup_logging",
    "validate_database"
]


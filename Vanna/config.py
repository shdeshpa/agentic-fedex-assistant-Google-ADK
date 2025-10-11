# =============================================================================
#  Filename: config.py
#
#  Short Description: Configuration and constants for Vanna FedEx system
#
#  Creation date: 2025-10-09
#  Author:  Shrinivas Deshpande
# =============================================================================

"""
Configuration module for Vanna FedEx Rate Query System.

Contains environment variables, constants, model paths, and configuration
settings extracted from the original vanna_ollama_sqlite_fedex.py file.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class VannaConfig:
    """Configuration class for Vanna FedEx system."""
    
    # Database configuration
    db_path: Path = Path("fedex_rates.db")
    
    # Ollama configuration
    model: str = "qwen2.5:3b"
    ollama_host: str = "http://localhost:11434"
    
    # Qdrant configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "fedex_rates_collection"
    
    # Model persistence
    models_dir: Path = Path("models")
    training_data_file: Path = Path("fedex_training.json")
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # Streamlit configuration
    streamlit_port: int = 8501
    streamlit_host: str = "0.0.0.0"
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Ensure models directory exists
        self.models_dir.mkdir(exist_ok=True)
        
        # Set default log file if not specified
        if self.log_file is None:
            self.log_file = self.models_dir / "vanna.log"


# Comprehensive training examples extracted from original file
TRAINING_EXAMPLES: List[Dict[str, str]] = [
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
    
    # Additional training examples for cheapest rate queries
    {
        "question": "What is the cheapest rate for Zone 5?",
        "sql": "SELECT MIN(FedEx_Express_Saver) as cheapest_rate FROM fedex_rates WHERE Zone = 5 AND FedEx_Express_Saver IS NOT NULL;"
    },
    {
        "question": "Find the cheapest shipping option for Zone 3",
        "sql": "SELECT MIN(FedEx_Express_Saver) as cheapest_rate FROM fedex_rates WHERE Zone = 3 AND FedEx_Express_Saver IS NOT NULL;"
    },
    {
        "question": "What's the lowest cost service for Zone 7?",
        "sql": "SELECT MIN(FedEx_Express_Saver) as lowest_cost FROM fedex_rates WHERE Zone = 7 AND FedEx_Express_Saver IS NOT NULL;"
    },
    {
        "question": "Show the most economical rate for Zone 4",
        "sql": "SELECT MIN(FedEx_Express_Saver) as economical_rate FROM fedex_rates WHERE Zone = 4 AND FedEx_Express_Saver IS NOT NULL;"
    },
    {
        "question": "What's the best value shipping for Zone 6?",
        "sql": "SELECT MIN(FedEx_Express_Saver) as best_value FROM fedex_rates WHERE Zone = 6 AND FedEx_Express_Saver IS NOT NULL;"
    },
    {
        "question": "Find cheapest Express Saver rate for Zone 2",
        "sql": "SELECT MIN(FedEx_Express_Saver) as cheapest_express_saver FROM fedex_rates WHERE Zone = 2 AND FedEx_Express_Saver IS NOT NULL;"
    },
    {
        "question": "What's the most affordable option for Zone 8?",
        "sql": "SELECT MIN(FedEx_Express_Saver) as most_affordable FROM fedex_rates WHERE Zone = 8 AND FedEx_Express_Saver IS NOT NULL;"
    },
]


# Database schema documentation
DATABASE_DOCUMENTATION = """
Database Documentation:

fedex_rates table:
- Contains shipping rates for all zones (2-8) and weights (1-150 lbs)
- 6 service columns: FedEx_First_Overnight, FedEx_Priority_Overnight, 
  FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver
- Zone: INTEGER (2-8)
- Weight: INTEGER (1-150 lbs)
- Each service column: REAL (rate in dollars)

CRITICAL SERVICE COST HIERARCHY (cheapest to most expensive):
1. FedEx_Express_Saver = CHEAPEST (3 days delivery)
2. FedEx_2Day = 2-day delivery
3. FedEx_2Day_AM = 2-day delivery (morning)
4. FedEx_Standard_Overnight = 1-day delivery
5. FedEx_Priority_Overnight = 1-day delivery (priority)
6. FedEx_First_Overnight = MOST EXPENSIVE (1-day, 8 AM delivery)

Key relationships:
- Zone determines shipping distance (higher zone = farther distance)
- Weight affects rate (heavier packages cost more)
- Services have different delivery speeds and costs
- Express_Saver is ALWAYS the cheapest option
- First_Overnight is ALWAYS the most expensive option

IMPORTANT: Always include Zone and Weight columns in SELECT statements when they are relevant to the query.
IMPORTANT: Use <= for "under X lbs" queries, not < .
IMPORTANT: Always include Zone column when querying by zone.
IMPORTANT: For "cheapest" queries, use MIN(FedEx_Express_Saver) as Express_Saver is always cheapest.
IMPORTANT: For "most expensive" queries, use MAX(FedEx_First_Overnight) as First_Overnight is always most expensive.
"""


# FedEx service types
FEDEX_SERVICE_TYPES = [
    "FedEx First Overnight",
    "FedEx Priority Overnight", 
    "FedEx Standard Overnight",
    "FedEx 2Day AM",
    "FedEx 2Day",
    "FedEx Express Saver"
]

# Zone range
ZONE_RANGE = list(range(2, 9))  # Zones 2-8

# Weight range
WEIGHT_RANGE = list(range(1, 151))  # 1-150 lbs


def get_config() -> VannaConfig:
    """Get configuration instance with environment variable overrides."""
    config = VannaConfig()
    
    # Override with environment variables if present
    config.db_path = Path(os.getenv("FEDEX_DB_PATH", config.db_path))
    config.model = os.getenv("OLLAMA_MODEL", config.model)
    config.ollama_host = os.getenv("OLLAMA_HOST", config.ollama_host)
    config.qdrant_host = os.getenv("QDRANT_HOST", config.qdrant_host)
    config.qdrant_port = int(os.getenv("QDRANT_PORT", config.qdrant_port))
    config.qdrant_collection = os.getenv("QDRANT_COLLECTION", config.qdrant_collection)
    config.log_level = os.getenv("LOG_LEVEL", config.log_level)
    
    return config


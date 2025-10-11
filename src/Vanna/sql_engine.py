# =============================================================================
#  Filename: sql_engine.py
#
#  Short Description: SQLite operations and schema introspection
#
#  Creation date: 2025-10-09
#  Author:  Shrinivas Deshpande
# =============================================================================

"""
SQL Engine for Vanna FedEx Rate Query System.

Handles SQLite connection, query execution, schema introspection,
and database operations extracted from the original vanna_ollama_sqlite_fedex.py file.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
from loguru import logger

from src.Vanna.config import VannaConfig


class SQLiteEngine:
    """
    SQLite database engine for FedEx rate queries.
    
    This class handles:
    - Database connection and management
    - Query execution with error handling
    - Schema introspection and DDL generation
    - Database statistics and validation
    """
    
    def __init__(self, config: VannaConfig):
        """
        Initialize the SQLite engine.
        
        Args:
            config: VannaConfig instance with database path
        """
        self.config = config
        self.connection: Optional[sqlite3.Connection] = None
        
        logger.info(f"Initializing SQLiteEngine with database: {config.db_path}")
    
    def connect(self) -> None:
        """Connect to the SQLite database."""
        try:
            if not self.config.db_path.exists():
                raise FileNotFoundError(f"Database file not found: {self.config.db_path}")
            
            self.connection = sqlite3.connect(str(self.config.db_path))
            # Enable row factory for named access
            self.connection.row_factory = sqlite3.Row
            
            logger.success(f"✅ Connected to database: {self.config.db_path}")
            
            # Test connection with a simple query
            self.execute_query("SELECT COUNT(*) as count FROM fedex_rates")
            
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.success("✅ Database connection closed")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame with query results
            
        Raises:
            sqlite3.Error: If query execution fails
            RuntimeError: If not connected to database
        """
        if not self.connection:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        try:
            logger.debug(f"Executing query: {query[:100]}...")
            df = pd.read_sql_query(query, self.connection)
            logger.debug(f"Query returned {len(df)} rows")
            return df
            
        except sqlite3.Error as e:
            logger.error(f"❌ Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def execute_safe_query(self, query: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Execute a SQL query safely, returning results and any error message.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple of (DataFrame or None, error message or None)
        """
        try:
            df = self.execute_query(query)
            return df, None
        except Exception as e:
            return None, str(e)
    
    def get_table_names(self) -> List[str]:
        """
        Get list of all table names in the database.
        
        Returns:
            List of table names
        """
        df = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        return df['name'].tolist()
    
    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """
        Get schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            DataFrame with schema information
        """
        return self.execute_query(f"PRAGMA table_info({table_name})")
    
    def get_table_ddl(self, table_name: str) -> str:
        """
        Generate DDL (CREATE TABLE) statement for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            DDL statement as string
        """
        schema_df = self.get_table_schema(table_name)
        
        columns = []
        for _, row in schema_df.iterrows():
            col_def = f"{row['name']} {row['type']}"
            if row['notnull']:
                col_def += " NOT NULL"
            if row['pk']:
                col_def += " PRIMARY KEY"
            columns.append(col_def)
        
        ddl = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
        return ddl
    
    def get_record_count(self, table_name: str) -> int:
        """
        Get total number of records in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of records
        """
        df = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
        return df.iloc[0, 0]
    
    def get_distinct_values(self, table_name: str, column_name: str) -> List[Any]:
        """
        Get distinct values from a specific column.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            
        Returns:
            List of distinct values
        """
        df = self.execute_query(f"SELECT DISTINCT {column_name} FROM {table_name} ORDER BY {column_name}")
        return df[column_name].tolist()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        stats = {}
        
        try:
            # Get table names
            tables = self.get_table_names()
            stats['tables'] = tables
            
            # Get record counts for each table
            record_counts = {}
            for table in tables:
                record_counts[table] = self.get_record_count(table)
            stats['record_counts'] = record_counts
            
            # FedEx-specific stats
            if 'fedex_rates' in tables:
                fedex_stats = self._get_fedex_specific_stats()
                stats.update(fedex_stats)
            
            logger.info(f"📊 Database statistics collected: {len(tables)} tables")
            
        except Exception as e:
            logger.error(f"❌ Failed to collect database statistics: {e}")
            stats['error'] = str(e)
        
        return stats
    
    def _get_fedex_specific_stats(self) -> Dict[str, Any]:
        """Get FedEx-specific database statistics."""
        fedex_stats = {}
        
        try:
            # Zone statistics
            zones = self.get_distinct_values('fedex_rates', 'Zone')
            fedex_stats['zones'] = sorted(zones)
            fedex_stats['zone_count'] = len(zones)
            
            # Weight statistics
            weights = self.get_distinct_values('fedex_rates', 'Weight')
            fedex_stats['weights'] = sorted(weights)
            fedex_stats['weight_count'] = len(weights)
            fedex_stats['min_weight'] = min(weights)
            fedex_stats['max_weight'] = max(weights)
            
            # Service column statistics
            service_columns = [
                'FedEx_First_Overnight', 'FedEx_Priority_Overnight',
                'FedEx_Standard_Overnight', 'FedEx_2Day_AM',
                'FedEx_2Day', 'FedEx_Express_Saver'
            ]
            
            service_stats = {}
            for service in service_columns:
                # Count non-null values for this service
                df = self.execute_query(f"SELECT COUNT(*) as count FROM fedex_rates WHERE {service} IS NOT NULL")
                service_stats[service] = df.iloc[0, 0]
            
            fedex_stats['service_coverage'] = service_stats
            
            # Price range statistics
            price_stats = {}
            for service in service_columns:
                df = self.execute_query(f"""
                    SELECT 
                        MIN({service}) as min_price,
                        MAX({service}) as max_price,
                        AVG({service}) as avg_price
                    FROM fedex_rates 
                    WHERE {service} IS NOT NULL
                """)
                if not df.empty:
                    price_stats[service] = {
                        'min': df.iloc[0, 0],
                        'max': df.iloc[0, 1],
                        'avg': df.iloc[0, 2]
                    }
            
            fedex_stats['price_ranges'] = price_stats
            
            logger.info(f"📊 FedEx statistics: {len(zones)} zones, {len(weights)} weights")
            
        except Exception as e:
            logger.error(f"❌ Failed to collect FedEx statistics: {e}")
            fedex_stats['error'] = str(e)
        
        return fedex_stats
    
    def validate_database(self) -> Dict[str, bool]:
        """
        Validate database structure and data integrity.
        
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        try:
            # Check if fedex_rates table exists
            tables = self.get_table_names()
            validation['fedex_rates_exists'] = 'fedex_rates' in tables
            
            if 'fedex_rates' in tables:
                # Check required columns
                schema_df = self.get_table_schema('fedex_rates')
                columns = schema_df['name'].tolist()
                
                required_columns = ['Zone', 'Weight']
                service_columns = [
                    'FedEx_First_Overnight', 'FedEx_Priority_Overnight',
                    'FedEx_Standard_Overnight', 'FedEx_2Day_AM',
                    'FedEx_2Day', 'FedEx_Express_Saver'
                ]
                
                validation['has_required_columns'] = all(col in columns for col in required_columns)
                validation['has_service_columns'] = all(col in columns for col in service_columns)
                
                # Check data ranges
                zones = self.get_distinct_values('fedex_rates', 'Zone')
                weights = self.get_distinct_values('fedex_rates', 'Weight')
                
                validation['valid_zone_range'] = all(2 <= zone <= 8 for zone in zones)
                validation['valid_weight_range'] = all(1 <= weight <= 150 for weight in weights)
                validation['has_data'] = len(zones) > 0 and len(weights) > 0
                
                # Check for null primary key values
                null_zone_count = self.execute_query("SELECT COUNT(*) as count FROM fedex_rates WHERE Zone IS NULL").iloc[0, 0]
                null_weight_count = self.execute_query("SELECT COUNT(*) as count FROM fedex_rates WHERE Weight IS NULL").iloc[0, 0]
                
                validation['no_null_primary_keys'] = null_zone_count == 0 and null_weight_count == 0
            
            # Overall validation
            validation['database_valid'] = all(validation.values())
            
            logger.info(f"🔍 Database validation: {'✅ PASSED' if validation['database_valid'] else '❌ FAILED'}")
            
        except Exception as e:
            logger.error(f"❌ Database validation failed: {e}")
            validation['error'] = str(e)
            validation['database_valid'] = False
        
        return validation
    
    def get_sample_data(self, table_name: str = 'fedex_rates', limit: int = 5) -> pd.DataFrame:
        """
        Get sample data from a table.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to return
            
        Returns:
            DataFrame with sample data
        """
        return self.execute_query(f"SELECT * FROM {table_name} LIMIT {limit}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def create_sql_engine(config: VannaConfig) -> SQLiteEngine:
    """
    Factory function to create and connect a SQLite engine.
    
    Args:
        config: VannaConfig instance
        
    Returns:
        Connected SQLiteEngine instance
    """
    engine = SQLiteEngine(config)
    engine.connect()
    return engine


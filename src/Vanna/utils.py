# =============================================================================
#  Filename: utils.py
#
#  Short Description: Logging, validation, and helper functions
#
#  Creation date: 2025-10-09
#  Author:  Shrinivas Deshpande
# =============================================================================

"""
Utility functions for Vanna FedEx Rate Query System.

Contains logging setup, validation functions, and helper utilities
extracted from the original vanna_ollama_sqlite_fedex.py file.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from loguru import logger

from src.Vanna.config import VannaConfig


def setup_logging(config: VannaConfig) -> None:
    """
    Setup logging configuration using loguru.
    
    Args:
        config: VannaConfig instance with logging settings
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=config.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler if log file is specified
    if config.log_file:
        logger.add(
            config.log_file,
            level=config.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days"
        )
    
    logger.info(f"Logging configured with level: {config.log_level}")


def validate_database(config: VannaConfig) -> Tuple[bool, List[str]]:
    """
    Validate that the database exists and has the expected structure.
    
    Args:
        config: VannaConfig instance
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check if database file exists
    if not config.db_path.exists():
        errors.append(f"Database file not found: {config.db_path}")
        return False, errors
    
    # Try to connect and validate structure
    try:
        import sqlite3
        conn = sqlite3.connect(str(config.db_path))
        
        # Check if fedex_rates table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fedex_rates'")
        if not cursor.fetchone():
            errors.append("fedex_rates table not found in database")
        
        # Check required columns
        cursor = conn.execute("PRAGMA table_info(fedex_rates)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['Zone', 'Weight']
        service_columns = [
            'FedEx_First_Overnight', 'FedEx_Priority_Overnight',
            'FedEx_Standard_Overnight', 'FedEx_2Day_AM',
            'FedEx_2Day', 'FedEx_Express_Saver'
        ]
        
        missing_columns = []
        for col in required_columns + service_columns:
            if col not in columns:
                missing_columns.append(col)
        
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check if table has data
        cursor = conn.execute("SELECT COUNT(*) FROM fedex_rates")
        count = cursor.fetchone()[0]
        if count == 0:
            errors.append("fedex_rates table is empty")
        
        conn.close()
        
    except Exception as e:
        errors.append(f"Database validation error: {e}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_ollama_connection(config: VannaConfig) -> Tuple[bool, str]:
    """
    Validate that Ollama is running and the model is available.
    
    Args:
        config: VannaConfig instance
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        import requests
        
        # Check if Ollama server is running
        response = requests.get(f"{config.ollama_host}/api/tags", timeout=5)
        if response.status_code != 200:
            return False, f"Ollama server not responding at {config.ollama_host}"
        
        # Check if model is available
        models = response.json().get('models', [])
        model_names = [model['name'] for model in models]
        
        if config.model not in model_names:
            return False, f"Model '{config.model}' not found. Available models: {model_names}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Ollama validation error: {e}"


def validate_qdrant_connection(config: VannaConfig) -> Tuple[bool, str]:
    """
    Validate that Qdrant is running and accessible.
    
    Args:
        config: VannaConfig instance
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        import requests
        
        # Check if Qdrant server is running
        response = requests.get(f"http://{config.qdrant_host}:{config.qdrant_port}/collections", timeout=5)
        if response.status_code != 200:
            return False, f"Qdrant server not responding at {config.qdrant_host}:{config.qdrant_port}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Qdrant validation error: {e}"


def validate_system(config: VannaConfig) -> Dict[str, Any]:
    """
    Comprehensive system validation.
    
    Args:
        config: VannaConfig instance
        
    Returns:
        Dictionary with validation results
    """
    validation_results = {
        'database': {'valid': False, 'errors': []},
        'ollama': {'valid': False, 'error': ''},
        'qdrant': {'valid': False, 'error': ''},
        'overall': {'valid': False, 'summary': ''}
    }
    
    logger.info("🔍 Starting system validation...")
    
    # Validate database
    db_valid, db_errors = validate_database(config)
    validation_results['database']['valid'] = db_valid
    validation_results['database']['errors'] = db_errors
    
    # Validate Ollama
    ollama_valid, ollama_error = validate_ollama_connection(config)
    validation_results['ollama']['valid'] = ollama_valid
    validation_results['ollama']['error'] = ollama_error
    
    # Validate Qdrant
    qdrant_valid, qdrant_error = validate_qdrant_connection(config)
    validation_results['qdrant']['valid'] = qdrant_valid
    validation_results['qdrant']['error'] = qdrant_error
    
    # Overall validation
    all_valid = db_valid and ollama_valid and qdrant_valid
    validation_results['overall']['valid'] = all_valid
    
    if all_valid:
        validation_results['overall']['summary'] = "All systems validated successfully"
        logger.success("✅ System validation passed")
    else:
        validation_results['overall']['summary'] = "Some systems failed validation"
        logger.error("❌ System validation failed")
    
    return validation_results


def save_test_results(results: List[Dict[str, Any]], output_file: Path) -> None:
    """
    Save test results to a JSON file.
    
    Args:
        results: List of test results
        output_file: Path to output file
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"💾 Test results saved to {output_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save test results: {e}")


def load_test_results(input_file: Path) -> List[Dict[str, Any]]:
    """
    Load test results from a JSON file.
    
    Args:
        input_file: Path to input file
        
    Returns:
        List of test results
    """
    try:
        with open(input_file, 'r') as f:
            results = json.load(f)
        logger.info(f"📂 Test results loaded from {input_file}")
        return results
    except Exception as e:
        logger.error(f"❌ Failed to load test results: {e}")
        return []


def format_query_results(df, max_rows: int = 10) -> str:
    """
    Format query results for display.
    
    Args:
        df: DataFrame with query results
        max_rows: Maximum number of rows to display
        
    Returns:
        Formatted string representation
    """
    if df is None or df.empty:
        return "No results found."
    
    # Limit rows for display
    display_df = df.head(max_rows)
    
    # Create formatted output
    output = []
    output.append(f"Query returned {len(df)} row(s)")
    
    if len(df) > max_rows:
        output.append(f"Showing first {max_rows} rows:")
    
    output.append("")
    output.append(display_df.to_string(index=False))
    
    return "\n".join(output)


def create_test_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a summary of test results.
    
    Args:
        results: List of test results
        
    Returns:
        Summary dictionary
    """
    if not results:
        return {'total_tests': 0, 'passed': 0, 'failed': 0, 'success_rate': 0.0}
    
    total_tests = len(results)
    passed = sum(1 for r in results if r.get('success', False))
    failed = total_tests - passed
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0.0
    
    return {
        'total_tests': total_tests,
        'passed': passed,
        'failed': failed,
        'success_rate': success_rate,
        'timestamp': datetime.now().isoformat()
    }


def print_validation_report(validation_results: Dict[str, Any]) -> None:
    """
    Print a formatted validation report.
    
    Args:
        validation_results: Validation results dictionary
    """
    print("\n" + "="*70)
    print("🔍 SYSTEM VALIDATION REPORT")
    print("="*70)
    
    # Database validation
    db_result = validation_results['database']
    status = "✅ PASS" if db_result['valid'] else "❌ FAIL"
    print(f"\n📊 Database: {status}")
    if not db_result['valid']:
        for error in db_result['errors']:
            print(f"   • {error}")
    
    # Ollama validation
    ollama_result = validation_results['ollama']
    status = "✅ PASS" if ollama_result['valid'] else "❌ FAIL"
    print(f"\n🤖 Ollama: {status}")
    if not ollama_result['valid']:
        print(f"   • {ollama_result['error']}")
    
    # Qdrant validation
    qdrant_result = validation_results['qdrant']
    status = "✅ PASS" if qdrant_result['valid'] else "❌ FAIL"
    print(f"\n🗄️ Qdrant: {status}")
    if not qdrant_result['valid']:
        print(f"   • {qdrant_result['error']}")
    
    # Overall result
    overall_result = validation_results['overall']
    status = "✅ ALL SYSTEMS GO" if overall_result['valid'] else "❌ SYSTEM ISSUES"
    print(f"\n🎯 Overall: {status}")
    print(f"   {overall_result['summary']}")
    
    print("="*70 + "\n")


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'timestamp': datetime.now().isoformat()
    }


def check_dependencies() -> Dict[str, bool]:
    """
    Check if all required dependencies are available.
    
    Returns:
        Dictionary with dependency availability
    """
    dependencies = {}
    
    try:
        import pandas
        dependencies['pandas'] = True
    except ImportError:
        dependencies['pandas'] = False
    
    try:
        import vanna
        dependencies['vanna'] = True
    except ImportError:
        dependencies['vanna'] = False
    
    try:
        import sqlite3
        dependencies['sqlite3'] = True
    except ImportError:
        dependencies['sqlite3'] = False
    
    try:
        import requests
        dependencies['requests'] = True
    except ImportError:
        dependencies['requests'] = False
    
    try:
        from loguru import logger
        dependencies['loguru'] = True
    except ImportError:
        dependencies['loguru'] = False
    
    return dependencies


# =============================================================================
#  Filename: fedex_main.py
#
#  Short Description: Unified entry script for modular Vanna FedEx system
#
#  Creation date: 2025-10-09
#  Author:  Shrinivas Deshpande
# =============================================================================

"""
Unified Entry Script for Modular Vanna FedEx Rate Query System.

This script provides the main entry point that replicates the functionality
of the original vanna_ollama_sqlite_fedex.py file but uses the modular structure.

Usage:
    python fedex_main.py                    # Interactive mode
    python fedex_main.py --streamlit        # Streamlit web interface
    python fedex_main.py --test             # Run validation tests
    python fedex_main.py --validate         # System validation only
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from loguru import logger

# Add Vanna package to path
sys.path.insert(0, str(Path(__file__).parent))

from Vanna import (
    VannaConfig, VannaModelManager, SQLiteEngine, 
    TextToSQLEngine, StreamlitApp,
    setup_logging, validate_system, print_validation_report
)


class FedExMainApp:
    """
    Main application class that orchestrates the modular components.
    
    This class replicates the functionality of the original VannaFedExRates class
    but uses the modular architecture.
    """
    
    def __init__(self, config: Optional[VannaConfig] = None):
        """
        Initialize the main application.
        
        Args:
            config: Optional VannaConfig instance. If None, uses default config.
        """
        self.config = config or VannaConfig()
        self.engine: Optional[TextToSQLEngine] = None
        
        # Setup logging
        setup_logging(self.config)
        
        logger.info("\n" + "="*70)
        logger.info("🚀 MODULAR VANNA FEDEX RATE QUERY SYSTEM")
        logger.info("="*70 + "\n")
    
    def validate_system(self) -> bool:
        """
        Validate that all required systems are available.
        
        Returns:
            True if all systems are valid, False otherwise
        """
        logger.info("🔍 Validating system requirements...")
        
        validation_results = validate_system(self.config)
        print_validation_report(validation_results)
        
        return validation_results['overall']['valid']
    
    def initialize(self) -> None:
        """Initialize the text-to-SQL engine."""
        try:
            logger.info("🔧 Initializing modular components...")
            
            # Initialize the text-to-SQL engine
            self.engine = TextToSQLEngine(self.config)
            self.engine.initialize()
            
            logger.success("✅ Modular system initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    def interactive_loop(self) -> None:
        """
        Run interactive text-to-SQL loop.
        
        This replicates the interactive_loop() method from the original file.
        """
        if not self.engine:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        
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
                df = self.engine.query(question)
                
                if df is not None:
                    print("\n📦 Results:")
                    print(df.to_string(index=False))
                    print(f"\nRows returned: {len(df)}")
                else:
                    logger.warning("⚠️ No results returned")
                    
            except KeyboardInterrupt:
                logger.info("\n👋 Session interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
    
    def _show_help(self) -> None:
        """Display comprehensive example questions."""
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
    
    def run_example_tests(self) -> None:
        """
        Run example test queries to validate training.
        
        This replicates the run_example_tests() method from the original file.
        """
        if not self.engine:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        
        logger.info("\n🧪 Running example test queries...")
        
        test_queries = [
            "Show all rates for Zone 2",
            "What are the FedEx 2Day rates for 10 lbs?",
            "Compare overnight services for Zone 5",
            "Find the cheapest rate for Zone 3, 15 lbs"
        ]
        
        for query in test_queries:
            self.engine.test_query(query)
            print()  # Add spacing between tests
    
    def run_streamlit(self) -> None:
        """Run the Streamlit web interface."""
        logger.info("🌐 Starting Streamlit web interface...")
        
        try:
            import streamlit.web.cli as stcli
            import sys
            
            # Set up streamlit arguments
            sys.argv = [
                "streamlit",
                "run",
                str(Path(__file__).parent / "Vanna" / "ui_app.py"),
                "--server.port", str(self.config.streamlit_port),
                "--server.address", self.config.streamlit_host,
                "--server.headless", "true"
            ]
            
            # Run streamlit
            stcli.main()
            
        except Exception as e:
            logger.error(f"❌ Failed to start Streamlit: {e}")
            logger.info("Make sure Streamlit is installed: pip install streamlit")
    
    def close(self) -> None:
        """Close connections and cleanup resources."""
        if self.engine:
            self.engine.close()
        logger.success("✅ Application closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Modular Vanna FedEx Rate Query System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fedex_main.py                    # Interactive mode
  python fedex_main.py --streamlit        # Streamlit web interface
  python fedex_main.py --test             # Run validation tests
  python fedex_main.py --validate         # System validation only
        """
    )
    
    parser.add_argument(
        "--streamlit", 
        action="store_true", 
        help="Run Streamlit web interface"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run example test queries"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate system requirements only"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file (not implemented)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create main application
        app = FedExMainApp()
        
        # Validate system
        if not app.validate_system():
            logger.error("❌ System validation failed. Please fix the issues above.")
            return 1
        
        # If only validation requested, exit here
        if args.validate:
            logger.success("✅ System validation completed successfully")
            return 0
        
        # Initialize the system
        app.initialize()
        
        # Run requested mode
        if args.streamlit:
            app.run_streamlit()
        elif args.test:
            app.run_example_tests()
        else:
            # Interactive mode (default)
            app.interactive_loop()
        
        # Cleanup
        app.close()
        
        logger.info("\n" + "="*70)
        logger.success("✅ SESSION ENDED")
        logger.info("="*70 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n👋 Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Make sure Ollama is running: ollama serve")
        logger.info("2. Check model is available: ollama pull qwen2.5:3b")
        logger.info("3. Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
        logger.info("4. Ensure fedex_rates.db exists in the project root")
        return 1


if __name__ == "__main__":
    sys.exit(main())



# =============================================================================
#  Filename: test_vanna.py
#
#  Short Description: Test script for Vanna FedEx rate query system
#
#  Creation date: 2025-10-10
#  Author:  Shrinivas Deshpande
# =============================================================================

from Vanna import VannaConfig, TextToSQLEngine

# Initialize
config = VannaConfig()
engine = TextToSQLEngine(config)
engine.initialize()

# Query in natural language
results = engine.query("What is cheapest rate for zone 2, 10 lbs")
print(results)

# Or use Streamlit UI
# from Vanna import run_streamlit_app
# run_streamlit_app()  # Opens browser with chat interface


#!/bin/bash

# =============================================================================
#  Filename: run_app.sh
#
#  Short Description: Launch script for unified FedEx shipping application
#
#  Creation date: 2025-10-10
#  Author:  Shrinivas Deshpande
# =============================================================================

echo "🚀 Starting FedEx Shipping Assistant..."
echo "=================================="

# Check if Ollama is running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "⚠️  Ollama is not running. Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Check if Qdrant is running
if ! nc -z localhost 6333; then
    echo "⚠️  Qdrant is not running. Please start Qdrant on port 6333"
    echo "   You can start it with: docker run -p 6333:6333 qdrant/qdrant"
    exit 1
fi

# Check if database exists
if [ ! -f "fedex_rates.db" ]; then
    echo "❌ fedex_rates.db not found. Please ensure the database is created."
    exit 1
fi

echo "✅ All services are running"
echo "🌐 Starting Streamlit application..."
echo ""

# Launch the application
uv run streamlit run fedex_app.py --server.port 8505 --server.address 0.0.0.0

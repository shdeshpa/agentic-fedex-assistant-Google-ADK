#!/bin/bash

# =============================================================================
#  Filename: switch_llm.sh
#
#  Short Description: Switch between OpenAI and Ollama LLM providers
#
#  Creation date: 2025-10-11
#  Author: Shrinivas Deshpande
# =============================================================================

echo "🔄 FedEx Shipping Assistant - LLM Provider Switcher"
echo "=================================================="
echo ""
echo "Choose your LLM provider:"
echo "  1) OpenAI (GPT-4o-mini) - Fast, cloud-based, requires API key"
echo "  2) Ollama (qwen2.5:7b) - Free, local, requires Ollama running"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo "✅ Switching to OpenAI..."
        sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=openai/' .env
        echo "✅ LLM_PROVIDER set to 'openai'"
        echo ""
        echo "⚠️  Make sure your OPENAI_API_KEY is set in .env file!"
        echo "    Edit .env and set: OPENAI_API_KEY=sk-your-key-here"
        ;;
    2)
        echo "✅ Switching to Ollama..."
        sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env
        echo "✅ LLM_PROVIDER set to 'ollama'"
        echo ""
        echo "⚠️  Make sure Ollama is running: ollama serve"
        echo "    And model is pulled: ollama pull qwen2.5:7b"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Current .env configuration:"
grep "^LLM_PROVIDER=" .env
grep "^OPENAI_MODEL=" .env
grep "^OLLAMA_SQL_MODEL=" .env
echo ""
echo "✅ Provider switched! Restart the app for changes to take effect."
echo "   Run: ./run_app.sh"


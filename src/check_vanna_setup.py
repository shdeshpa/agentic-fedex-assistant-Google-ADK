# =============================================================================
#  Filename: check_vanna_setup.py
#
#  Short Description: Verify Vanna + Ollama setup is ready
#
#  Creation date: 2025-10-08
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Quick verification script to check if Vanna + Ollama setup is ready.
"""

import sqlite3
import sys
from pathlib import Path

import requests
from loguru import logger


def check_database() -> bool:
    """Check if SQLite database exists and is accessible."""
    logger.info("1️⃣  Checking SQLite database...")
    
    db_path = Path(__file__).parent.parent / "fedex_rates.db"
    
    if not db_path.exists():
        logger.error(f"   ❌ Database not found: {db_path}")
        logger.info("   💡 Run: uv run python src/load_to_sqlite.py")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fedex_rates")
        count = cursor.fetchone()[0]
        conn.close()
        
        logger.success(f"   ✅ Database OK ({count:,} records)")
        return True
    except Exception as e:
        logger.error(f"   ❌ Database error: {e}")
        return False


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    logger.info("2️⃣  Checking Ollama service...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            logger.success(f"   ✅ Ollama is running ({len(models)} models available)")
            return True
        else:
            logger.error(f"   ❌ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("   ❌ Cannot connect to Ollama")
        logger.info("   💡 Start Ollama: ollama serve")
        return False
    except Exception as e:
        logger.error(f"   ❌ Unexpected error: {e}")
        return False


def check_ollama_models() -> bool:
    """Check if required LLM models are available."""
    logger.info("3️⃣  Checking available models...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models_data]
            
            if not model_names:
                logger.warning("   ⚠️  No models installed")
                logger.info("   💡 Pull a model: ollama pull llama3")
                return False
            
            logger.success("   ✅ Available models:")
            for name in model_names:
                logger.info(f"      • {name}")
            
            # Check for recommended models
            recommended = ["llama3", "mistral", "phi3"]
            has_recommended = any(
                any(rec in name for rec in recommended) 
                for name in model_names
            )
            
            if has_recommended:
                logger.success("   ✅ Found recommended model")
            else:
                logger.warning("   ⚠️  Consider installing: llama3, mistral, or phi3")
            
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"   ❌ Error checking models: {e}")
        return False


def check_qdrant_running() -> bool:
    """Check if Qdrant service is running."""
    logger.info("4️⃣  Checking Qdrant service...")
    
    try:
        response = requests.get("http://localhost:6333/collections", timeout=5)
        if response.status_code == 200:
            collections = response.json().get("result", {}).get("collections", [])
            logger.success(f"   ✅ Qdrant is running ({len(collections)} collections)")
            return True
        else:
            logger.error(f"   ❌ Qdrant returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("   ❌ Cannot connect to Qdrant")
        logger.info("   💡 Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
        return False
    except Exception as e:
        logger.error(f"   ❌ Unexpected error: {e}")
        return False


def check_vanna_import() -> bool:
    """Check if Vanna can be imported."""
    logger.info("5️⃣  Checking Vanna package...")
    
    try:
        from vanna.ollama import Ollama
        from vanna.qdrant import Qdrant_VectorStore
        logger.success("   ✅ Vanna package available (with Qdrant & Ollama support)")
        return True
    except ImportError as e:
        logger.error(f"   ❌ Cannot import Vanna: {e}")
        logger.info("   💡 Install: uv add vanna")
        return False


def main() -> None:
    """Run all setup checks."""
    logger.info("\n" + "="*70)
    logger.info("🔍 VANNA + OLLAMA SETUP VERIFICATION")
    logger.info("="*70 + "\n")
    
    checks = [
        ("Database", check_database),
        ("Ollama Service", check_ollama_running),
        ("LLM Models", check_ollama_models),
        ("Qdrant Service", check_qdrant_running),
        ("Vanna Package", check_vanna_import),
    ]
    
    results = []
    
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
        print()
    
    # Summary
    logger.info("="*70)
    logger.info("📊 SUMMARY")
    logger.info("="*70 + "\n")
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status}  {name}")
    
    print()
    
    if all_passed:
        logger.success("="*70)
        logger.success("✅ ALL CHECKS PASSED - READY TO USE VANNA!")
        logger.success("="*70)
        logger.info("\n🚀 Run: uv run python src/vanna_ollama_sqlite_fedex.py\n")
        sys.exit(0)
    else:
        logger.warning("="*70)
        logger.warning("⚠️  SOME CHECKS FAILED - SETUP INCOMPLETE")
        logger.warning("="*70)
        logger.info("\n📖 See VANNA_SETUP_GUIDE.md for help\n")
        sys.exit(1)


if __name__ == "__main__":
    main()


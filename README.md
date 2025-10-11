# 🚚 FedEx Rate Assistant

A comprehensive FedEx shipping rate lookup system with AI-powered natural language query capabilities.

---

## 🎯 **Quick Start**

### **View Training Examples:**
```bash
uv run python src/fedex_vanna/train_vanna.py --show-examples
```

### **Run Fast Streamlit App:**
```bash
uv run streamlit run fast_streamlit_app.py --server.port=8502
```
**Access**: http://localhost:8502

### **Run Main Vanna-powered App:**
```bash
./start_chatbot.sh
```
**Access**: http://localhost:8502

---

## 📁 **Project Structure**

```
/home/shrini/fedex/
├── src/
│   ├── fedex_vanna/              # Vanna AI modules
│   │   ├── database.py           # Database operations
│   │   ├── vanna_manager.py      # Vanna initialization
│   │   ├── training.py           # Training examples
│   │   ├── query_handler.py      # Query processing
│   │   ├── cli.py                # CLI interface
│   │   ├── train_vanna.py        # View training examples
│   │   ├── test_vanna_accuracy.py # Validation tests
│   │   ├── check_vanna_persistence.py # Check Qdrant
│   │   └── validate_failed_queries.py # Analyze failures
│   ├── vanna_app.py              # Main Vanna application
│   └── vanna_ollama_sqlite_fedex.py # Original implementation
├── fast_streamlit_app.py         # Fast UI (no Vanna training)
├── app.py                         # Main Streamlit app
├── fedex_rates.db                 # SQLite database
├── docs/
│   └── vanna.md                   # Vanna specification
└── *.md                           # Documentation files
```

---

## 🚀 **Key Commands**

### **Training & Validation:**
```bash
# View all 35 training examples:
uv run python src/fedex_vanna/train_vanna.py --show-examples

# View by category:
uv run python src/fedex_vanna/train_vanna.py --categories

# Check Qdrant persistence:
uv run python src/fedex_vanna/check_vanna_persistence.py

# Run full validation test:
uv run python src/fedex_vanna/test_vanna_accuracy.py

# Analyze failed queries:
uv run python src/fedex_vanna/validate_failed_queries.py
```

### **Clear & Retrain:**
```bash
# Clear Qdrant collections:
uv run python3 -c "
from qdrant_client import QdrantClient
c = QdrantClient(host='localhost', port=6333)
for coll in ['sql', 'ddl', 'documentation']:
    c.delete_collection(coll)
"

# Restart app (will retrain):
./start_chatbot.sh
```

---

## 📊 **Current Status**

### **Database:**
- ✅ 1,050 records (7 zones × 150 weights)
- ✅ 6 service types (First Overnight to Express Saver)
- ✅ SQLite database: `fedex_rates.db`

### **Training:**
- ✅ 35 training examples
- ✅ 53 examples stored in Qdrant
- ✅ Schema + Documentation trained

### **Validation:**
- ✅ 24/35 queries passing (68.6%)
- ❌ 11/35 queries need improvement
- 🎯 Target: >90% accuracy

---

## 📚 **Documentation**

### **Essential Docs:**
1. **VANNA_COMMANDS_CHEATSHEET.md** - Quick command reference
2. **VANNA_VALIDATION_REPORT.md** - Test results & analysis
3. **TASK_COMPLETION_SUMMARY.md** - Recent work summary
4. **docs/vanna.md** - Original specification

### **Status Files:**
- `APP_STATUS.md` - Application status
- `WORKING_APPS.md` - Which apps are working
- Various `*_FIX_STATUS.md` files - Fix histories

---

## 🎨 **Applications**

### **1. Fast Streamlit App** (Recommended)
- **File**: `fast_streamlit_app.py`
- **Features**: Fast, direct SQL queries, beautiful UI
- **Launch**: `uv run streamlit run fast_streamlit_app.py --server.port=8502`
- **Access**: http://localhost:8502

### **2. Vanna-powered Streamlit App**
- **File**: `app.py`
- **Features**: AI-powered text-to-SQL
- **Launch**: `./start_chatbot.sh`
- **Access**: http://localhost:8502
- **Note**: Requires Ollama + Qdrant running

### **3. Flask SQL App** (Backup)
- **File**: `fedex_sql_app.py`
- **Features**: Simple Flask interface
- **Launch**: `uv run python fedex_sql_app.py`
- **Access**: http://localhost:8085

---

## 🔧 **Dependencies**

### **Required Services:**
- ✅ Ollama (LLM) - http://localhost:11434
- ✅ Qdrant (Vector DB) - http://localhost:6333

### **Python Packages:**
- Core: `streamlit`, `pandas`, `sqlite3`
- Vanna: `vanna`, `qdrant-client`
- LLM: `ollama`

Install with:
```bash
uv sync
```

---

## 📖 **Example Queries**

### **Zone-based:**
- "What are all the rates for Zone 2?"
- "Show rates for Zone 3 under 10 lbs"
- "Compare FedEx 2Day rates across all zones for 10 lbs"

### **Weight-based:**
- "What are the rates for 5 lb packages?"
- "Show rates for packages between 10 and 20 lbs"

### **Service Comparisons:**
- "Show FedEx Priority Overnight rates for Zone 5"
- "What's the cheapest service for Zone 6, 15 lbs?"

### **Analysis:**
- "Show average rates by zone for FedEx 2Day service"
- "Find the most expensive rates for each zone"

---

## 🐛 **Common Issues**

### **Issue: Blank screen in Streamlit**
```bash
# Solution: Clear browser cache or try different port
pkill -f "streamlit run"
uv run streamlit run fast_streamlit_app.py --server.port=8503
```

### **Issue: Vanna not returning results**
```bash
# Solution: Check Qdrant and retrain
uv run python src/fedex_vanna/check_vanna_persistence.py
# If needed, clear and retrain
```

### **Issue: Database not found**
```bash
# Check database exists:
ls -lh fedex_rates.db
# If missing, extract from PDF
```

---

## 🎯 **Next Steps (To Improve Accuracy)**

1. **Update Training Examples** - Integrate improved examples
2. **Clear Qdrant** - Remove old training data
3. **Retrain** - Train with improved examples
4. **Validate** - Re-run tests, target >90% accuracy

See `VANNA_VALIDATION_REPORT.md` for detailed analysis.

---

## 📞 **Quick Reference**

```bash
# Most useful commands:
uv run python src/fedex_vanna/train_vanna.py --show-examples
uv run streamlit run fast_streamlit_app.py --server.port=8502
uv run python src/fedex_vanna/check_vanna_persistence.py
./start_chatbot.sh
```

---

## ✅ **Status**

**Last Updated**: 2025-10-09

**Current State**:
- ✅ Database extracted and loaded
- ✅ 35 training examples ready
- ✅ Fast Streamlit app working
- ✅ Vanna app working (68.6% accuracy)
- ✅ All files organized in `src/fedex_vanna/`

**Next**: Improve Vanna accuracy from 68.6% to >90%

---

For detailed information, see the documentation files listed above.
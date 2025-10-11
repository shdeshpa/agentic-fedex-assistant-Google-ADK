# Quick Start Guide - FedEx LangGraph Shipping Assistant

## 🚀 Get Started in 3 Steps

### Step 1: Prerequisites Check

Ensure these services are running:

```bash
# Check Ollama (should return model list)
curl http://localhost:11434/api/tags

# Check Qdrant (should return empty list or collections)
curl http://localhost:6333/collections

# Check database exists
ls fedex_rates.db
```

**Not running?** Start them:
```bash
# Start Ollama
ollama serve

# Pull model if needed
ollama pull qwen2.5:3b

# Qdrant should be running on port 6333
# (Installation varies by platform)
```

### Step 2: Run the App

```bash
# Simple - use the run script
./run_langgraph_app.sh

# Or directly with uv
uv run streamlit run fedex_langgraph_app.py
```

The app will open at: **http://localhost:8501**

### Step 3: Try Example Queries

Copy-paste these into the chat:

```
Ship 15 lb box from Fremont, CA to New York, NY. Budget $200
```

```
What's the cheapest way to ship 10 lbs to Zone 5?
```

```
Compare overnight options for 25 lbs
```

## 🎯 What You'll See

1. **User Query** → Your question
2. **Multi-Agent Processing** → Agents working together
3. **Shipping Option** → Service, Cost, Delivery time
4. **Agent Reflection** → Quality check (expandable)
5. **Generated SQL** → Database query (expandable)
6. **Rate Data** → Full results (expandable, downloadable)
7. **Supervisor Review** → If cost ≥ $1000 or requested

## 🤖 The Agents

- **FedEx Response Agent** 💼 - Understands your request
- **SQL Query Agent** 🔍 - Queries the database  
- **Reflection Node** 🤔 - Checks recommendation quality
- **Supervisor Agent** 👨‍💼 - Reviews complex cases

## 💡 Tips

- **Be specific**: Include weight, zones, or budget
- **Be natural**: Ask like you're talking to a person
- **Request supervisor**: Add "need supervisor review"
- **Compare options**: Ask for comparisons

## 🔧 Troubleshooting

### "Workflow initialization failed"
- Start Ollama: `ollama serve`
- Start Qdrant on port 6333
- Check database exists: `ls fedex_rates.db`

### "No results found"
- Check your zone and weight values
- Try simpler queries first
- Check database has data

### Import errors
```bash
uv sync
```

## 📚 Learn More

- Full docs: See `LANGGRAPH_README.md`
- Agent details: See `agents/` folder
- Workflow: See `agents/workflow.py`

---

**That's it! You're ready to query FedEx rates with AI.** 🚀


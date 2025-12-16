# Agentic AI FedEx Shipping Assistant

> **Multi-Agent System with Full Reasoning Transparency**

A production-ready **Agentic AI** system that transforms shipping rate lookups into intelligent, transparent conversations. This project demonstrates modern multi-agent architecture with explicit reasoning trajectories, reflection patterns, and tool-based decision making.

---

## Why Agentic AI?

Traditional chatbots are **black boxes** - you ask a question, you get an answer, but you have no idea *why*. This creates trust issues in enterprise applications where decisions have financial impact.

### The Agentic Difference

| Traditional AI | Agentic AI (This Project) |
|---------------|---------------------------|
| Single monolithic LLM call | Multi-agent orchestration |
| Hidden reasoning | Transparent trajectory logging |
| No self-assessment | Reflection pattern with confidence scores |
| Hardcoded logic | Dynamic tool selection |
| Override user intent | **Respect user intent** (critical!) |

**Key Principle**: If a user asks for "overnight" shipping, we recommend overnight - not the cheapest option. **User intent takes priority over cost optimization.**

---

## Multi-Agent Architecture

```
                              ┌─────────────────────────────┐
                              │         USER QUERY          │
                              │ "Ship chocolates overnight  │
                              │   from SFO to Denver"       │
                              └─────────────┬───────────────┘
                                            │
                    ┌───────────────────────▼───────────────────────┐
                    │            🛡️ SUPERVISOR AGENT                │
                    │                                                │
                    │  • Prompt injection detection                  │
                    │  • Request validation                          │
                    │  • Security guardrails                         │
                    │  • Routes to appropriate agent                 │
                    │                                                │
                    │  Reflection: "Valid shipping query, 90%        │
                    │               confidence, routing to customer" │
                    └───────────────────────┬───────────────────────┘
                                            │
                    ┌───────────────────────▼───────────────────────┐
                    │        💬 CUSTOMER INTERACTION AGENT          │
                    │                                                │
                    │  • Parse natural language query                │
                    │  • Extract: origin, destination, weight        │
                    │  • Detect urgency: "overnight" → overnight     │
                    │  • Recognize: SFO → San Francisco, CA          │
                    │                                                │
                    │  Reflection: "Understood request - overnight   │
                    │               delivery, 85% confidence"        │
                    └───────────────────────┬───────────────────────┘
                                            │
                    ┌───────────────────────▼───────────────────────┐
                    │         📦 SHIPPING EXPERT AGENT              │
                    │                                                │
                    │  Tools Available:                              │
                    │  ┌────────────────────────────────────────┐   │
                    │  │ 🗺️ Zone Calculator                      │   │
                    │  │   SFO → San Francisco → Zone 3         │   │
                    │  └────────────────────────────────────────┘   │
                    │  ┌────────────────────────────────────────┐   │
                    │  │ ⚖️ Weight Estimator                     │   │
                    │  │   "chocolates" → 2.0 lbs (high conf)   │   │
                    │  └────────────────────────────────────────┘   │
                    │  ┌────────────────────────────────────────┐   │
                    │  │ 💾 Rate Database (Vanna SQL)           │   │
                    │  │   Zone 3, 2 lbs → Real FedEx rates     │   │
                    │  └────────────────────────────────────────┘   │
                    │                                                │
                    │  Reflection: "User asked for overnight,        │
                    │               recommending Standard Overnight  │
                    │               at $44.68 - respecting intent"   │
                    └───────────────────────┬───────────────────────┘
                                            │
                              ┌─────────────▼───────────────┐
                              │      RESPONSE + TRAJECTORY  │
                              │  • Recommendation with why  │
                              │  • Full reasoning log       │
                              │  • Agent reflections        │
                              │  • All alternatives shown   │
                              └─────────────────────────────┘
```

---

## Key Features

### 1. Transparent Reasoning Trajectory

Every query produces a visible decision trail:

```
[Supervisor] >>> Agent Supervisor started
[Supervisor] [REFLECT] Valid shipping query, 90% confidence
[Supervisor] [TRANSFER] -> Customer Interaction: Valid shipping query

[Customer]   >>> Agent Customer Interaction started
[Customer]   [REFLECT] Extracted: origin=SFO, dest=Denver, urgency=overnight
[Customer]   [TRANSFER] -> Shipping Expert: Request parsed

[Expert]     >>> Agent Shipping Expert started
[Expert]     [TOOL] Calling zone_calculator: {origin: "SFO", dest: "Denver"}
[Expert]     [TOOL] zone_calculator returned: Zone 3
[Expert]     [TOOL] Calling weight_estimator: {item: "chocolates"}
[Expert]     [TOOL] weight_estimator returned: 2.0 lbs
[Expert]     [REFLECT] Recommending overnight per user intent, 90% confidence
```

### 2. Reflection Pattern

Each agent provides self-assessment:

```python
{
    "agent": "Shipping Expert",
    "understanding": "Ship 2 lbs overnight from SF to Denver",
    "actions_taken": [
        "Calculated zone: 3",
        "Estimated weight: 2.0 lbs",
        "Found overnight options",
        "Selected best overnight per user intent"
    ],
    "confidence_percent": 90,
    "concerns": []
}
```

### 3. Intent-Aware Recommendations

**Critical Design Decision**: User intent > cost optimization

| User Says | System Recommends | NOT |
|-----------|-------------------|-----|
| "overnight" | FedEx Standard Overnight $44.68 | ~~Cheapest at $24.83~~ |
| "cheapest" | FedEx Express Saver $24.83 | N/A |
| "2-day" | FedEx 2Day $26.68 | ~~Overnight~~ |
| No preference | Cheapest option | N/A |

### 4. Intelligent Location Resolution

```python
# Airport Codes
"SFO" → "San Francisco, CA"
"JFK" → "New York, NY"
"ORD" → "Chicago, IL"

# City Nicknames
"Big Apple" → "New York, NY"
"Windy City" → "Chicago, IL"

# Typo Correction (LLM-powered)
"San Fransisco" → "San Francisco"
"Los Angels" → "Los Angeles"
```

### 5. Weight Estimation

```python
# Common items database + LLM fallback
"wine bottle" → 3.0 lbs (high confidence)
"65 inch TV" → 55.0 lbs (high confidence)
"chocolates" → 2.0 lbs (high confidence)
"vintage vase" → 8.0 lbs (medium confidence, LLM estimate)
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Framework** | Custom (Google ADK patterns) | Multi-agent orchestration |
| **Tools** | FastMCP | Zone calculator, weight estimator |
| **LLM** | OpenAI GPT-4o-mini | Reasoning, parsing, correction |
| **Text-to-SQL** | Vanna.AI + ChromaDB | Database queries |
| **Database** | SQLite | 1,050 FedEx rate records |
| **Frontend** | NiceGUI | Modern Python web UI |
| **Logging** | Loguru + JSON | Trajectory persistence |

---

## Project Structure

```
fedex-shipping-assistant/
├── fedex_app_agentic.py          # Multi-agent UI (port 8083)
├── fedex_app_nicegui.py          # Legacy UI (port 8082)
├── fedex_rates.db                # SQLite database
│
├── src/
│   ├── agents/
│   │   ├── adk_agents.py         # Multi-agent system
│   │   │   ├── SupervisorAgent   # Security & routing
│   │   │   ├── CustomerAgent     # Query understanding
│   │   │   └── ExpertAgent       # Tool execution
│   │   ├── session_manager.py    # State management
│   │   └── unified_agent.py      # Legacy agent
│   │
│   ├── tools/
│   │   ├── zone_calculator.py    # Location → Zone
│   │   ├── weight_estimator.py   # Item → Weight
│   │   └── mcp_server.py         # FastMCP tools
│   │
│   ├── logging/
│   │   └── trajectory_logger.py  # Reasoning logs
│   │
│   └── Vanna/
│       ├── model_manager.py      # Text-to-SQL setup
│       └── config.py             # Training examples
│
└── logs/                         # JSON trajectory files
    └── trajectory_YYYYMMDD.jsonl
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/agentic-fedex-assistant.git
cd agentic-fedex-assistant

# Install dependencies
uv sync

# Configure environment
echo "LLM_PROVIDER=openai" > .env
echo "OPENAI_API_KEY=your-key-here" >> .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env

# Run the agentic application
python fedex_app_agentic.py
```

### Access
Open http://localhost:8083 in your browser.

---

## Example Queries

### Intent-Specific
- **"Ship chocolates overnight from SFO to Denver"**
  - Detects: overnight intent, SFO → San Francisco
  - Recommends: FedEx Standard Overnight (respects intent)

- **"Cheapest way to send 10 lbs to New York"**
  - Detects: cheapest intent
  - Recommends: FedEx Express Saver (lowest cost)

### With Budget
- **"Send wine bottles to Boston, budget $50"**
  - Estimates: wine bottles ≈ 3 lbs
  - Filters: Only options under $50
  - Warns: If intent (overnight) exceeds budget

### Complex
- **"Ship a 65 inch TV from Big Apple to LA"**
  - Resolves: Big Apple → New York, NY
  - Estimates: 65" TV → 55 lbs
  - Returns: All options sorted by price

---

## Agentic AI Patterns Implemented

### 1. Multi-Agent Orchestration
Three specialized agents with clear responsibilities, communicating via state transfer.

### 2. Tool Use
Agents dynamically invoke tools (zone calculator, weight estimator, database) based on task needs.

### 3. Reflection
Every agent outputs a self-assessment with confidence scores and concerns.

### 4. Trajectory Logging
Complete decision trail saved to console and JSON files for debugging and audit.

### 5. Intent Preservation
User preferences are detected and respected, not overridden by optimization logic.

### 6. Graceful Degradation
If Vanna fails, direct SQL fallback. If that fails, clear error message (no hallucinated rates).

---

## Comparison: Before vs After

| Aspect | Before (Unified Agent) | After (Agentic) |
|--------|----------------------|-----------------|
| Architecture | Single agent | 3 specialized agents |
| Reasoning | Hidden | Transparent trajectory |
| User Intent | Often overridden | **Always respected** |
| Tool Use | Hardcoded flow | Dynamic selection |
| Errors | Silent failures | Explicit logging |
| Debugging | Difficult | Full trajectory JSON |
| Confidence | None shown | Per-agent reflection |

---

## Metrics

| Metric | Value |
|--------|-------|
| **Response Time** | 3-5 seconds |
| **Agent Handoffs** | 3 (Supervisor → Customer → Expert) |
| **Tools Available** | 3 (zone, weight, database) |
| **Training Examples** | 38 (Vanna text-to-SQL) |
| **Rate Records** | 1,050 |
| **Reflection Coverage** | 100% of agents |

---

## Future Enhancements

- [ ] **Memory**: Cross-session conversation history
- [ ] **Learning**: Improve from user corrections
- [ ] **Multi-carrier**: Add UPS, USPS agents
- [ ] **Voice**: Speech-to-text input
- [ ] **API**: REST endpoints for integration

---

## About This Project

This project demonstrates **Agentic AI** development skills:

- **Multi-Agent Design**: Specialized agents with clear boundaries
- **Transparent AI**: Visible reasoning for trust and debugging
- **User-Centric**: Intent detection and preservation
- **Production Patterns**: Reflection, trajectory logging, graceful degradation

### Author

**Shrinivas Deshpande**

- GitHub: [@shdeshpa](https://github.com/shdeshpa)
- LinkedIn: [Connect](https://linkedin.com/in/shrinivas-deshpande)

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

### Keywords

`Agentic AI` `Multi-Agent Systems` `LLM Orchestration` `Transparent AI` `Reflection Pattern` `Tool Use` `Intent Detection` `FastMCP` `Vanna.AI` `Text-to-SQL` `Python` `NiceGUI` `OpenAI` `Enterprise AI` `Shipping Automation`

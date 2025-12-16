# Agentic AI FedEx Shipping Assistant

> **Enterprise-Ready Multi-Agent System with Full Reasoning Transparency**

A production-grade **Agentic AI** system that transforms shipping rate lookups into intelligent, transparent conversations. This project demonstrates the intersection of **Product Management thinking** and **cutting-edge AI engineering** - from user problem identification through multi-agent orchestration with explicit reasoning trajectories.

---

## Executive Summary

| What | How |
|------|-----|
| **Problem** | Black-box AI systems erode enterprise trust - users don't know *why* they got an answer |
| **Solution** | Multi-agent architecture with transparent reasoning at every step |
| **Differentiator** | User intent preservation - AI recommends what user *asked for*, not what's cheapest |
| **Tech Stack** | Google ADK patterns, FastMCP tools, Vanna.AI text-to-SQL, COSTAR prompt engineering |

---

## Product Management Perspective

### Problem Identification

Traditional shipping rate chatbots suffer from three critical failures:

1. **Trust Deficit**: Users receive answers without understanding the reasoning
2. **Intent Override**: Systems optimize for cheapest options, ignoring user preferences
3. **Data Quality**: Manual rate entry leads to errors and outdated information

### User-Centric Solution

```
User Need                          → System Feature
────────────────────────────────────────────────────────
"Why did you recommend this?"      → Transparent reasoning trajectory
"I said overnight, not cheapest!"  → Intent-aware recommendations
"Is this price accurate?"          → Real FedEx rates from official guide
"Can I trust this AI?"             → Agent reflection with confidence scores
```

### Success Metrics

| Metric | Target | Implementation |
|--------|--------|----------------|
| **Reasoning Visibility** | 100% of decisions explained | Trajectory logging to console + JSON |
| **Intent Accuracy** | User preference respected | Urgency detection with service mapping |
| **Data Freshness** | Official FedEx rates | COSTAR-extracted from FedEx Service Guide |
| **Agent Confidence** | Self-assessed accuracy | Reflection pattern with % confidence |

---

## Technical Architecture

### Multi-Agent Orchestration (Google ADK Patterns)

```
                              ┌─────────────────────────────┐
                              │         USER QUERY          │
                              │ "Ship chocolates overnight  │
                              │   from SFO to Denver"       │
                              └─────────────┬───────────────┘
                                            │
                    ┌───────────────────────▼───────────────────────┐
                    │            SUPERVISOR AGENT                   │
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
                    │        CUSTOMER INTERACTION AGENT             │
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
                    │         SHIPPING EXPERT AGENT                 │
                    │                                                │
                    │  Tools Available:                              │
                    │  ┌────────────────────────────────────────┐   │
                    │  │ Zone Calculator                         │   │
                    │  │   SFO → San Francisco → Zone 3         │   │
                    │  └────────────────────────────────────────┘   │
                    │  ┌────────────────────────────────────────┐   │
                    │  │ Weight Estimator                        │   │
                    │  │   "chocolates" → 2.0 lbs (high conf)   │   │
                    │  └────────────────────────────────────────┘   │
                    │  ┌────────────────────────────────────────┐   │
                    │  │ Rate Database (Vanna SQL)              │   │
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

## Key Innovations

### 1. COSTAR Prompt Engineering for Data Extraction

The system uses **COSTAR framework** (Context, Objective, Style, Tone, Audience, Response) to extract 1,050 shipping rates from FedEx's official PDF Service Guide.

```python
# COSTAR-based extraction prompt
EXTRACTION_PROMPT = """
CONTEXT: You are analyzing FedEx Express Rate Tables from the official
FedEx Service Guide 2024. The tables span pages 13-33 and contain zone-based
pricing for weights 1-150 lbs across 6 service types.

OBJECTIVE: Extract structured rate data with 100% accuracy. Handle:
- Multi-line cells in PDF tables
- Zone headers (2-8)
- Service types: First Overnight, Priority Overnight, Standard Overnight,
  2Day AM, 2Day, Express Saver

STYLE: Precise, systematic extraction. Validate each cell against expected
format (currency values $X.XX).

TONE: Technical accuracy is paramount - these rates affect business decisions.

AUDIENCE: Database system that will serve customer queries.

RESPONSE FORMAT:
{
    "zone": int,
    "weight": int,
    "service_type": str,
    "rate": float
}
"""
```

**Result**: 1,050 accurate rate records across 6 service types, 8 zones, and weights 1-150 lbs.

### 2. Vanna.AI Text-to-SQL with RAG

Instead of hardcoding SQL queries, the system uses **Vanna.AI** with 38 training examples to generate accurate SQL dynamically.

```python
# Training example from src/Vanna/config.py
{
    "question": "What's the cheapest overnight option for 5 lbs to zone 4?",
    "sql": """
        SELECT Zone, Weight, FedEx_Standard_Overnight as cheapest_overnight
        FROM fedex_rates
        WHERE Zone = 4 AND Weight = 5
    """
}
```

**Vanna Architecture**:
```
User Question → Vanna (RAG) → Generated SQL → SQLite → Results → LLM → Natural Response
                   ↑
         ChromaDB Vector Store
         (38 training examples)
```

**Database Schema (Wide Format)**:
| Zone | Weight | FedEx_First_Overnight | FedEx_Priority_Overnight | FedEx_Standard_Overnight | FedEx_2Day_AM | FedEx_2Day | FedEx_Express_Saver |
|------|--------|----------------------|-------------------------|-------------------------|--------------|-----------|-------------------|
| 2 | 1 | $64.35 | $51.21 | $44.22 | $28.28 | $26.24 | $24.83 |
| 3 | 2 | $68.84 | $54.35 | $44.68 | $29.14 | $26.68 | $25.29 |

### 3. Intent-Aware Recommendations

**Critical Design Decision**: User intent takes priority over cost optimization.

```python
# From src/agents/adk_agents.py
def _analyze_options(self, rates, budget, urgency):
    """
    IMPORTANT: User intent takes priority over cost optimization.
    If user asks for overnight, recommend overnight - don't override with cheapest.
    """

    # PRIMARY RECOMMENDATION: Based on user's expressed intent
    if urgency and urgency.lower() not in ['standard', 'none', '']:
        target_services = self.urgency_service_map.get(urgency_lower)
        if target_services:
            matching_rates = [r for r in rates if r.get('service_type') in target_services]
            # Recommend WHAT USER ASKED FOR, then show alternatives
```

| User Says | System Recommends | Why |
|-----------|-------------------|-----|
| "overnight" | FedEx Standard Overnight $44.68 | Respects user intent |
| "cheapest" | FedEx Express Saver $24.83 | Optimizes for cost |
| "2-day" | FedEx 2Day $26.68 | Matches delivery speed |
| No preference | Cheapest option | Safe default |

### 4. Transparent Reasoning Trajectory

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

### 5. Agent Reflection Pattern

Each agent provides structured self-assessment:

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

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Agent Framework** | Custom (Google ADK patterns) | Multi-agent orchestration with state transfer |
| **Tools** | FastMCP | Zone calculator, weight estimator |
| **LLM** | OpenAI GPT-4o-mini | Reasoning, parsing, correction |
| **Text-to-SQL** | Vanna.AI + ChromaDB | RAG-based SQL generation with 38 examples |
| **Database** | SQLite | 1,050 FedEx rate records |
| **Data Extraction** | COSTAR Prompting | PDF → Structured data |
| **Frontend** | NiceGUI | Modern Python web UI |
| **Logging** | Loguru + JSON Lines | Trajectory persistence |

---

## Project Structure

```
fedex-shipping-assistant/
├── fedex_app_agentic.py          # Multi-agent UI (port 8083)
├── fedex_rates.db                # SQLite with 1,050 rates
│
├── src/
│   ├── agents/
│   │   ├── adk_agents.py         # Multi-agent system
│   │   │   ├── SupervisorAgent   # Security & routing
│   │   │   ├── CustomerAgent     # Query understanding
│   │   │   └── ExpertAgent       # Tool execution + Vanna SQL
│   │   ├── session_manager.py    # State management
│   │   └── unified_agent.py      # Legacy single-agent
│   │
│   ├── tools/
│   │   ├── zone_calculator.py    # Location → Zone (handles SFO, typos)
│   │   ├── weight_estimator.py   # Item → Weight (LLM-powered)
│   │   └── mcp_server.py         # FastMCP tool definitions
│   │
│   ├── logging/
│   │   └── trajectory_logger.py  # Console + JSON trajectory
│   │
│   ├── Vanna/
│   │   ├── model_manager.py      # Vanna.AI setup
│   │   └── config.py             # 38 training examples
│   │
│   └── extract_fedex_rates.py    # COSTAR PDF extraction
│
└── logs/
    └── trajectory_YYYYMMDD.jsonl # Reasoning audit trail
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key

### Installation

```bash
# Clone repository
git clone https://github.com/shdeshpa/agentic-fedex-assistant-Google-ADK.git
cd agentic-fedex-assistant-Google-ADK

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
  - Returns: All options sorted by user preference

---

## Agentic AI Patterns Demonstrated

| Pattern | Implementation |
|---------|----------------|
| **Multi-Agent Orchestration** | 3 specialized agents with state transfer |
| **Tool Use** | Dynamic invocation of zone/weight/SQL tools |
| **Reflection** | Per-agent self-assessment with confidence |
| **Trajectory Logging** | Complete decision audit in JSON |
| **Intent Preservation** | User preferences over cost optimization |
| **Graceful Degradation** | Vanna fallback → Direct SQL → Clear error |
| **Security Guards** | Prompt injection detection at Supervisor |

---

## Before vs After

| Aspect | Traditional Chatbot | This Agentic System |
|--------|--------------------|--------------------|
| Architecture | Single LLM call | 3 specialized agents |
| Reasoning | Hidden black box | Transparent trajectory |
| User Intent | Often overridden | **Always respected** |
| Tool Use | Hardcoded flow | Dynamic selection |
| Errors | Silent failures | Explicit logging |
| Debugging | Difficult | Full JSON trail |
| Confidence | Not shown | Per-agent reflection |
| Data | Manual entry | COSTAR extraction |
| SQL | Hardcoded queries | Vanna RAG generation |

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Response Time** | 3-5 seconds |
| **Agent Handoffs** | 3 per query |
| **Tools Available** | 3 (zone, weight, database) |
| **Vanna Training Examples** | 38 |
| **Rate Records** | 1,050 |
| **Service Types** | 6 |
| **Zones Covered** | 2-8 |
| **Weight Range** | 1-150 lbs |

---

## Future Roadmap

- [ ] **Memory**: Cross-session conversation history
- [ ] **Learning**: Improve from user corrections
- [ ] **Multi-carrier**: Add UPS, USPS agents
- [ ] **Voice**: Speech-to-text input
- [ ] **API**: REST endpoints for integration
- [ ] **Analytics**: Dashboard for trajectory analysis

---

## Skills Demonstrated

### Product Management
- Problem identification and user need analysis
- Success metrics definition and measurement
- User-centric feature prioritization
- Technical requirement specification

### Agentic AI Engineering
- Multi-agent system design (Google ADK patterns)
- Tool/function calling with FastMCP
- Reflection and self-assessment patterns
- Trajectory logging for auditability

### Prompt Engineering
- COSTAR framework for data extraction
- Few-shot learning for Vanna training
- Intent detection prompting
- Error handling and fallback prompts

### Data Engineering
- PDF → Structured data pipeline
- Text-to-SQL with RAG (Vanna + ChromaDB)
- SQLite schema design for rate lookup
- JSON Lines logging for analysis

---

## Author

**Shrinivas Deshpande**

- GitHub: [@shdeshpa](https://github.com/shdeshpa)
- LinkedIn: [Connect](https://linkedin.com/in/shrinivas-deshpande)

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

### Keywords

`Agentic AI` `Multi-Agent Systems` `LLM Orchestration` `Google ADK` `FastMCP` `Vanna.AI` `Text-to-SQL` `COSTAR Prompting` `Prompt Engineering` `Transparent AI` `Reflection Pattern` `Intent Detection` `ChromaDB` `RAG` `Python` `NiceGUI` `OpenAI` `Enterprise AI` `Product Management`

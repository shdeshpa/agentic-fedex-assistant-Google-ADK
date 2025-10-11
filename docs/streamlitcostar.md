
⸻

COSTAR Prompt: LangGraph-Based FedEx Shipping Advisor (Multi-Agent, Portable)

Context

You are building a LangGraph-based multi-agent workflow that powers a Streamlit chatbot to answer FedEx shipping rate queries.

This system helps users ship packages from any U.S. location (e.g., Fremont, CA, Austin, TX, or Boston, MA) to any domestic destination by querying a local SQLite database (fedex_rates.db) that contains 2025 FedEx rate tables.

The application uses Ollama or VannaAI for text-to-SQL translation, reasoning, and reflection.
It will have three agents connected through a LangGraph state graph with shared memory and reasoning context.Make sure to look at files under src/Vanna folder. All Langgraph files should be under a separate folder. follow cursor rules. Add other tools or resources there and annotate the files approrpriately.

⸻

Objective

Build a LangGraph app that:
	1.	Interprets user shipping requests (origin, destination, weight, urgency, and budget).
	2.	Validates shipment legality (no live animals, perishables, explosives, or banned items).
	3.	Queries the rate database via a dedicated SQL Query Agent.
	4.	Reflects before replying — considering price tiers, transit times, and user budget.
	5.	Escalates to the Supervisor Agent if cost ≥ $1000 or on user request.
	6.	Runs inside a modern Streamlit chatbot UI with clear tables, history, and transparency.
	7.	Can be deployed anywhere (local MacBook, remote server, or cloud container) without location assumptions.

⸻

Agents

1. FedEx Response Agent

Role: Primary interface agent that interprets user intent and generates responses.
Goals:
	•	Understand source and destination from user input (using default current city if not given).
	•	Verify package eligibility (no illegal, fragile, or perishable goods).
	•	Estimate shipping cost and service options (Overnight, 2-Day, Express Saver, Ground).
	•	Reflect before replying to ensure suggestion fits customer’s budget and urgency.
	•	Trigger Supervisor if budget exceeded or user asks explicitly.

Tools:
	•	SQL Query Agent (delegates actual rate lookup).
	•	ReflectionNode (for self-evaluation before finalizing response).

Output Schema:

{
  "service": "FedEx Express Saver",
  "estimated_cost": 185.0,
  "delivery_days": 3,
  "recommendation": "Fits within stated budget. Best option for balance of cost and speed.",
  "supervisor_required": false
}


⸻

2. SQL Query Agent

Role: Specialized agent for safe, optimized SQL query execution.
Goals:
	•	Translate user context (weight, origin, destination, service type) into SQL.
	•	Use Ollama or VannaAI to generate natural-language → SQL mapping.
	•	Query fedex_rates.db and return rate tables.
	•	Validate SQL before execution to prevent injection or malformed queries.
	•	Return structured JSON to the calling agent.

Output Schema:

{
  "zone": "4",
  "service": "FedEx Express Saver",
  "weight_lb": 10,
  "cost_usd": 185.0,
  "delivery_days": 3
}


⸻

3. Supervisor Agent

Role: Oversight and escalation handler.
Triggers:
	•	Shipping cost ≥ $1000.
	•	User explicitly requests “Supervisor.”
Goals:
	•	Review conversation history and Response Agent’s reasoning.
	•	Validate fairness, accuracy, and budget alignment.
	•	Provide a calm, empathetic, final decision.
	•	Suggest next steps (e.g., alternative service, pickup scheduling, or split shipment).

Output Schema:

{
  "decision": "Confirm Express Saver recommendation",
  "reasoning": "Review shows Overnight cost exceeds stated budget. Express Saver fits best under $200.",
  "final_message": "After review, the Express Saver option remains optimal at $185, with 3-day delivery."
}


⸻

Style
	•	Use LangGraph for defining agents, nodes, and message flows.
	•	Use Streamlit for the conversational UI (st.chat_input, st.chat_message).
	•	Store state with st.session_state.
	•	Display tables for service, cost, and delivery time.
	•	Include visual cues for reflection and Supervisor intervention.
	•	Keep UI clean, mobile-friendly, and deployable on any environment.

⸻

Tasks
	1.	Initialize LangGraph
	•	Define nodes: UserInput, FedExResponseAgent, SQLQueryAgent, ReflectionNode, SupervisorAgent, and ResponseOutput.
	•	Define graph state schema:
origin, destination, weight, budget, illegal_item_flag, sql_query, rate_result, supervisor_required.
	2.	Build FedEx Response Agent
	•	Parse and validate user query.
	•	If missing origin, auto-detect or prompt user.
	•	Call SQL Query Agent for rate retrieval.
	•	Reflect internally before finalizing.
	•	Escalate to Supervisor if required.
	3.	Build SQL Query Agent
	•	Generate text-to-SQL via Ollama/Vanna.
	•	Execute safely on fedex_rates.db.
	•	Return structured rate result.
	4.	Build Reflection Node
	•	Ask: “Is my answer safe, lawful, budget-aligned, and clear?”
	•	If not, refine before sending downstream.
	5.	Build Supervisor Agent
	•	Review session context, re-run reasoning if needed.
	•	Provide empathetic and transparent decision.
	6.	Streamlit Interface
	•	Title: “FedEx LangGraph Shipping Assistant”
	•	Persistent chat history and reflections.
	•	Optional sidebar: service filters, weight sliders, origin auto-detect.
	•	Result: tabular display with service, rate, delivery time.
	•	Supervisor messages highlighted (different color or icon).

⸻

Action

Generate a Python file named fedex_langgraph_app.py that:
	•	Imports langgraph, streamlit, sqlite3, pandas, ollama or vanna.
	•	Defines agents, nodes, transitions, and shared memory.
	•	Connects to fedex_rates.db for querying.
	•	Runs full LangGraph workflow in a Streamlit chatbot UI.
	•	Executable via:

streamlit run fedex_langgraph_app.py


	•	Deployable anywhere — local or cloud (no city hard-coding).

⸻

Result

A multi-agent, self-reflective shipping assistant that:
	•	Works from any U.S. origin or deployment.
	•	Uses LangGraph for composable agent workflows.
	•	Handles user queries, SQL lookups, reflections, and supervisor escalations.
	•	Displays recommendations with reasoning and clarity.

⸻

Example Interactions

User: “Ship a 15 lb box from Fremont, CA to New York, NY. Budget $200.”
Response Agent: “FedEx Express Saver: $185, 3-day delivery. Fits your budget. Would you like to proceed?”

User: “Overnight option?”
Response Agent: “Overnight delivery is $410 — exceeds your budget. Shall I check with a Supervisor?”

User: “Yes.”
Supervisor: “Reviewed. Overnight cost is accurate at $410. Express Saver remains best within your $200 budget.”

User: “Can I ship frozen food?”
Response Agent: “No. FedEx prohibits shipping perishable items under standard services. Would you like to see dry-ice alternatives?”

⸻

Would you like me to now generate the LangGraph workflow diagram (nodes and edges) and the base Python code template for fedex_langgraph_app.py next?
That will let you drop it straight into Cursor and start implementing each agent.
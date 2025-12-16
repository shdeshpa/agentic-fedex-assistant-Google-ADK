"""
Google ADK-based Multi-Agent System for FedEx Shipping Assistant.

Implements a three-agent system:
1. Supervisor Agent - Security and routing
2. Customer Interaction Agent - Query understanding and refinement
3. Shipping Expert Agent - Rate lookup and recommendations

Uses Google ADK patterns for agent orchestration, state management,
and tool execution with FastMCP integration.
"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from src.tools.zone_calculator import ZoneCalculator
from src.tools.weight_estimator import WeightEstimator
from src.logging.trajectory_logger import TrajectoryLogger


class AgentType(str, Enum):
    """Types of agents in the system."""
    SUPERVISOR = "supervisor"
    CUSTOMER = "customer_interaction"
    EXPERT = "shipping_expert"


@dataclass
class AgentState:
    """State shared across agents."""
    session_id: str
    request_id: str
    user_query: str
    parsed_request: Optional[Dict[str, Any]] = None
    zone_result: Optional[Dict[str, Any]] = None
    weight_result: Optional[Dict[str, Any]] = None
    rate_results: Optional[List[Dict[str, Any]]] = None
    recommendation: Optional[Dict[str, Any]] = None
    trajectory: List[Dict[str, Any]] = field(default_factory=list)
    is_valid: bool = True
    validation_message: str = ""
    current_agent: AgentType = AgentType.SUPERVISOR
    reflection: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    next_agent: Optional[AgentType] = None
    is_final: bool = False
    reflection: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        llm_provider: str = "openai",
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        trajectory_logger: Optional[TrajectoryLogger] = None
    ):
        self.name = name
        self.agent_type = agent_type
        self.trajectory_logger = trajectory_logger

        # Initialize LLM
        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.1,
                api_key=api_key or os.getenv("OPENAI_API_KEY")
            )
        else:
            self.llm = ChatOllama(model=model, temperature=0.1)

        logger.info(f"Initialized {name} agent with {llm_provider}/{model}")

    @abstractmethod
    def process(self, state: AgentState) -> AgentResponse:
        """Process the current state and return response."""
        pass

    def _invoke_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke LLM with system and user prompts."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content

    def _log_reasoning(self, state: AgentState, reasoning: str):
        """Log reasoning step."""
        if self.trajectory_logger:
            self.trajectory_logger.log_reasoning(
                state.request_id,
                self.name,
                reasoning
            )

    def _log_reflection(self, state: AgentState, reflection: Dict[str, Any]):
        """Log reflection step."""
        if self.trajectory_logger:
            self.trajectory_logger.log_reflection(
                state.request_id,
                self.name,
                reflection
            )

    def _create_reflection(
        self,
        understanding: str,
        actions_taken: List[str],
        confidence: int,
        concerns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a reflection object."""
        return {
            "agent": self.name,
            "understanding": understanding,
            "actions_taken": actions_taken,
            "confidence_percent": confidence,
            "concerns": concerns or [],
            "summary": f"{self.name} processed with {confidence}% confidence"
        }


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Security and routing.

    Responsibilities:
    1. Detect prompt injection attempts
    2. Validate shipping-related queries
    3. Route valid requests to appropriate agents
    """

    SECURITY_PATTERNS = [
        "ignore previous",
        "ignore all previous",
        "disregard instructions",
        "new instructions",
        "system prompt",
        "you are now",
        "pretend to be",
        "act as if",
        "forget everything",
        "override",
        "bypass",
        "jailbreak"
    ]

    def __init__(self, **kwargs):
        super().__init__(
            name="Supervisor",
            agent_type=AgentType.SUPERVISOR,
            **kwargs
        )

    def process(self, state: AgentState) -> AgentResponse:
        """Validate and route the request."""
        start_time = time.time()

        if self.trajectory_logger:
            self.trajectory_logger.log_agent_start(
                state.request_id,
                self.name,
                {"query": state.user_query}
            )

        # Step 1: Check for prompt injection
        injection_detected = self._check_prompt_injection(state.user_query)

        if injection_detected:
            self._log_reasoning(
                state,
                f"Detected potential prompt injection in query"
            )

            reflection = self._create_reflection(
                understanding="Detected security threat in user query",
                actions_taken=["Analyzed query for injection patterns", "Blocked request"],
                confidence=95,
                concerns=["Possible prompt injection attempt"]
            )
            self._log_reflection(state, reflection)

            if self.trajectory_logger:
                self.trajectory_logger.log_agent_end(
                    state.request_id,
                    self.name,
                    {"status": "blocked", "reason": "prompt_injection"},
                    duration_ms=(time.time() - start_time) * 1000
                )

            return AgentResponse(
                success=False,
                message="I'm sorry, but I can't process that request. Please ask a shipping-related question.",
                is_final=True,
                reflection=reflection
            )

        # Step 2: Validate shipping-related query
        is_shipping_query = self._validate_shipping_query(state.user_query)

        if not is_shipping_query:
            self._log_reasoning(
                state,
                f"Query does not appear to be shipping-related"
            )

            reflection = self._create_reflection(
                understanding="Query is not related to shipping services",
                actions_taken=["Analyzed query intent", "Determined not shipping-related"],
                confidence=80,
                concerns=["User may need to rephrase their question"]
            )
            self._log_reflection(state, reflection)

            if self.trajectory_logger:
                self.trajectory_logger.log_agent_end(
                    state.request_id,
                    self.name,
                    {"status": "blocked", "reason": "not_shipping_related"},
                    duration_ms=(time.time() - start_time) * 1000
                )

            return AgentResponse(
                success=False,
                message="I'm a FedEx shipping assistant. I can help you with shipping rates, zones, and delivery options. How can I help you with shipping today?",
                is_final=True,
                reflection=reflection
            )

        # Step 3: Route to Customer Interaction Agent
        self._log_reasoning(
            state,
            "Query validated as shipping-related, routing to Customer Interaction Agent"
        )

        reflection = self._create_reflection(
            understanding="Valid shipping query detected",
            actions_taken=[
                "Checked for prompt injection",
                "Validated shipping intent",
                "Routing to customer interaction"
            ],
            confidence=90
        )
        self._log_reflection(state, reflection)

        if self.trajectory_logger:
            self.trajectory_logger.log_transfer(
                state.request_id,
                self.name,
                "Customer Interaction",
                "Valid shipping query"
            )
            self.trajectory_logger.log_agent_end(
                state.request_id,
                self.name,
                {"status": "validated", "next": "customer_interaction"},
                duration_ms=(time.time() - start_time) * 1000
            )

        state.is_valid = True
        return AgentResponse(
            success=True,
            message="Query validated",
            next_agent=AgentType.CUSTOMER,
            reflection=reflection
        )

    def _check_prompt_injection(self, query: str) -> bool:
        """Check for prompt injection patterns."""
        query_lower = query.lower()
        for pattern in self.SECURITY_PATTERNS:
            if pattern in query_lower:
                return True
        return False

    def _validate_shipping_query(self, query: str) -> bool:
        """Validate if query is shipping-related using LLM."""
        prompt = """Determine if this query is related to shipping services.

Query: "{query}"

Shipping-related queries include:
- Asking about shipping rates or prices
- Asking about delivery times
- Asking about zones
- Asking about package weight/dimensions
- Comparing shipping options
- Asking about FedEx services

Respond with ONLY "YES" or "NO"."""

        response = self._invoke_llm(
            "You are a query classifier. Respond only YES or NO.",
            prompt.format(query=query)
        )

        return "YES" in response.upper()


class CustomerInteractionAgent(BaseAgent):
    """
    Customer Interaction Agent - Query understanding.

    Responsibilities:
    1. Parse user query to extract shipping parameters
    2. Handle ambiguous requests with clarification
    3. Normalize inputs (cities, weights, etc.)
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Customer Interaction",
            agent_type=AgentType.CUSTOMER,
            **kwargs
        )

    def process(self, state: AgentState) -> AgentResponse:
        """Parse and understand the user query."""
        start_time = time.time()

        if self.trajectory_logger:
            self.trajectory_logger.log_agent_start(
                state.request_id,
                self.name,
                {"query": state.user_query}
            )

        # Parse the query using LLM
        parsed = self._parse_query(state.user_query)

        self._log_reasoning(
            state,
            f"Parsed query: origin={parsed.get('origin')}, "
            f"destination={parsed.get('destination')}, "
            f"weight={parsed.get('weight')}, "
            f"budget={parsed.get('budget')}"
        )

        # Validate required fields
        missing_fields = self._check_required_fields(parsed)

        if missing_fields:
            # Create clarification request
            reflection = self._create_reflection(
                understanding=f"Extracted some parameters but missing: {', '.join(missing_fields)}",
                actions_taken=["Parsed query", "Identified missing required fields"],
                confidence=60,
                concerns=[f"Need {field} to provide accurate quote" for field in missing_fields]
            )
            self._log_reflection(state, reflection)

            clarification = self._generate_clarification(missing_fields, parsed)

            if self.trajectory_logger:
                self.trajectory_logger.log_agent_end(
                    state.request_id,
                    self.name,
                    {"status": "needs_clarification", "missing": missing_fields},
                    duration_ms=(time.time() - start_time) * 1000
                )

            return AgentResponse(
                success=True,
                message=clarification,
                data={"parsed": parsed, "missing_fields": missing_fields},
                is_final=True,  # Need user response
                reflection=reflection
            )

        # Store parsed request in state
        state.parsed_request = parsed

        reflection = self._create_reflection(
            understanding=f"Understood request: Ship from {parsed['origin']} to {parsed['destination']}, {parsed['weight']} lbs",
            actions_taken=[
                "Parsed user query",
                "Extracted origin and destination",
                "Identified weight and urgency",
                "Checked for budget constraints"
            ],
            confidence=85
        )
        self._log_reflection(state, reflection)

        if self.trajectory_logger:
            self.trajectory_logger.log_transfer(
                state.request_id,
                self.name,
                "Shipping Expert",
                "Request parsed successfully"
            )
            self.trajectory_logger.log_agent_end(
                state.request_id,
                self.name,
                {"status": "parsed", "parsed_request": parsed},
                duration_ms=(time.time() - start_time) * 1000
            )

        return AgentResponse(
            success=True,
            message="Request parsed successfully",
            data={"parsed_request": parsed},
            next_agent=AgentType.EXPERT,
            reflection=reflection
        )

    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse shipping query using LLM."""
        prompt = f"""Parse this shipping request and extract key information.

User Request: "{query}"

Extract these parameters:
- origin: Origin city and state (if not mentioned, use "San Francisco, CA")
- destination: Destination city and state (required)
- weight: Package weight in pounds (if not mentioned, use null)
- budget: Maximum budget in USD (ONLY if explicitly mentioned, otherwise null)
- urgency: Delivery speed preference (see rules below)
- item_description: Description of items being shipped (if mentioned)

URGENCY DETECTION RULES (CRITICAL - respect user's delivery preference):
- "overnight", "next day", "next-day", "tomorrow", "urgent", "ASAP", "rush" → "overnight"
- "first overnight", "by 8am", "earliest" → "first"
- "priority overnight", "by 10:30am" → "priority"
- "2 day", "2-day", "two day", "in 2 days" → "2-day"
- "3 day", "express saver", "by end of week" → "express"
- "cheapest", "lowest cost", "budget", "economical" → "cheapest"
- If NO delivery preference mentioned → "standard"

IMPORTANT RULES:
1. Recognize airport codes: SFO = "San Francisco, CA", LAX = "Los Angeles, CA", JFK/NYC = "New York, NY", DEN = "Denver, CO", ORD = "Chicago, IL", BOS = "Boston, MA", SEA = "Seattle, WA", PHX = "Phoenix, AZ", ATL = "Atlanta, GA", DFW = "Dallas, TX", MIA = "Miami, FL"
2. Recognize city nicknames: "Big Apple" = "New York, NY", "Windy City" = "Chicago, IL", etc.
3. Always include state abbreviation with city (e.g., "Denver, CO" not just "Denver")
4. Only set budget if user explicitly mentions a dollar amount ($60, 60 dollars, etc.)
5. If they say "cheapest" or "best rate" without a number, set urgency to "cheapest" and budget to null
6. Extract item descriptions like "chocolates", "wine bottles", "TV" etc.

Return ONLY valid JSON with exactly these keys, no additional text:
{{"origin": "...", "destination": "...", "weight": null, "budget": null, "urgency": "standard", "item_description": null}}
"""

        response = self._invoke_llm(
            "You are a shipping request parser. Return only valid JSON.",
            prompt
        )

        try:
            # Clean up response
            response = response.strip()
            if response.startswith('```'):
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
                response = response.strip()

            parsed = json.loads(response)

            # Normalize values
            if parsed.get('budget') in ['None', 'null', '', 0]:
                parsed['budget'] = None
            if parsed.get('weight') in ['None', 'null', '', 0]:
                parsed['weight'] = None

            return parsed

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return {
                "origin": "San Francisco, CA",
                "destination": None,
                "weight": None,
                "budget": None,
                "urgency": "standard",
                "item_description": None
            }

    def _check_required_fields(self, parsed: Dict[str, Any]) -> List[str]:
        """Check for missing required fields."""
        missing = []
        if not parsed.get('destination'):
            missing.append('destination')
        # Weight can be estimated, so it's not strictly required
        return missing

    def _generate_clarification(
        self,
        missing_fields: List[str],
        parsed: Dict[str, Any]
    ) -> str:
        """Generate a clarification request."""
        clarifications = {
            'destination': "Where would you like to ship your package to?",
            'weight': "Could you tell me the approximate weight of your package?"
        }

        messages = []
        for field in missing_fields:
            if field in clarifications:
                messages.append(clarifications[field])

        if parsed.get('origin'):
            intro = f"I see you want to ship from {parsed['origin']}. "
        else:
            intro = "I'd be happy to help with your shipping needs. "

        return intro + " ".join(messages)


class ShippingExpertAgent(BaseAgent):
    """
    Shipping Expert Agent - Rate lookup and recommendations.

    Responsibilities:
    1. Calculate shipping zone using ZoneCalculator tool
    2. Estimate weight using WeightEstimator tool
    3. Query rate database
    4. Analyze options against budget
    5. Provide reasoned recommendations
    """

    def __init__(
        self,
        zone_calculator: Optional[ZoneCalculator] = None,
        weight_estimator: Optional[WeightEstimator] = None,
        vanna_client: Any = None,
        **kwargs
    ):
        super().__init__(
            name="Shipping Expert",
            agent_type=AgentType.EXPERT,
            **kwargs
        )

        # Initialize tools
        api_key = kwargs.get('api_key') or os.getenv("OPENAI_API_KEY")
        llm_provider = kwargs.get('llm_provider', 'openai')
        model = kwargs.get('model', 'gpt-4o-mini')

        self.zone_calculator = zone_calculator or ZoneCalculator(
            llm_provider=llm_provider,
            api_key=api_key,
            model=model
        )
        self.weight_estimator = weight_estimator or WeightEstimator(
            llm_provider=llm_provider,
            api_key=api_key,
            model=model
        )
        self.vanna_client = vanna_client

    def process(self, state: AgentState) -> AgentResponse:
        """Process shipping request and generate recommendations."""
        start_time = time.time()

        if self.trajectory_logger:
            self.trajectory_logger.log_agent_start(
                state.request_id,
                self.name,
                state.parsed_request
            )

        parsed = state.parsed_request
        if not parsed:
            return AgentResponse(
                success=False,
                message="No parsed request available",
                is_final=True
            )

        trajectory_steps = []

        # Step 1: Calculate Zone
        self._log_reasoning(state, "Calculating shipping zone...")

        if self.trajectory_logger:
            self.trajectory_logger.log_tool_call(
                state.request_id,
                self.name,
                "zone_calculator",
                {"origin": parsed['origin'], "destination": parsed['destination']}
            )

        zone_start = time.time()
        zone_result = self.zone_calculator.calculate_zone(
            origin=parsed['origin'],
            destination=parsed['destination']
        )
        zone_duration = (time.time() - zone_start) * 1000

        if self.trajectory_logger:
            self.trajectory_logger.log_tool_result(
                state.request_id,
                self.name,
                "zone_calculator",
                zone_result,
                duration_ms=zone_duration
            )

        state.zone_result = zone_result
        trajectory_steps.append({
            "tool": "zone_calculator",
            "result": zone_result
        })

        self._log_reasoning(
            state,
            f"Zone calculated: {zone_result['zone']} ({zone_result['reasoning']})"
        )

        # Step 2: Estimate Weight if needed
        weight = parsed.get('weight')
        if weight is None and parsed.get('item_description'):
            self._log_reasoning(state, "Estimating weight for items...")

            if self.trajectory_logger:
                self.trajectory_logger.log_tool_call(
                    state.request_id,
                    self.name,
                    "weight_estimator",
                    {"item_description": parsed['item_description']}
                )

            weight_start = time.time()
            weight_result = self.weight_estimator.estimate_weight(
                parsed['item_description']
            )
            weight_duration = (time.time() - weight_start) * 1000

            if self.trajectory_logger:
                self.trajectory_logger.log_tool_result(
                    state.request_id,
                    self.name,
                    "weight_estimator",
                    weight_result,
                    duration_ms=weight_duration
                )

            weight = weight_result['weight_lbs']
            state.weight_result = weight_result
            trajectory_steps.append({
                "tool": "weight_estimator",
                "result": weight_result
            })

            self._log_reasoning(
                state,
                f"Weight estimated: {weight} lbs ({weight_result['reasoning']})"
            )
        elif weight is None:
            # Default weight
            weight = 10.0
            self._log_reasoning(state, "Using default weight: 10 lbs")

        # Step 3: Query Rate Database
        self._log_reasoning(state, "Looking up shipping rates...")

        zone = zone_result.get('zone', 5)
        rates = self._query_rates(zone, weight, parsed.get('urgency', 'standard'))
        state.rate_results = rates
        trajectory_steps.append({
            "action": "rate_lookup",
            "zone": zone,
            "weight": weight,
            "rates_found": len(rates)
        })

        # Step 4: Analyze Budget
        budget = parsed.get('budget')
        recommendations = self._analyze_options(rates, budget, parsed.get('urgency'))

        # Step 5: Generate Response
        response_text = self._generate_response(
            parsed=parsed,
            zone_result=zone_result,
            weight=weight,
            rates=rates,
            recommendations=recommendations,
            budget=budget
        )

        state.recommendation = {
            "zone": zone,
            "weight": weight,
            "rates": rates,
            "recommendations": recommendations,
            "budget_analysis": self._analyze_budget_fit(rates, budget) if budget else None
        }

        reflection = self._create_reflection(
            understanding=f"Shipping {weight} lbs from {parsed['origin']} to {parsed['destination']} (Zone {zone})",
            actions_taken=[
                f"Calculated zone: {zone}",
                f"Determined weight: {weight} lbs",
                f"Found {len(rates)} rate options",
                f"Analyzed against budget: {'$' + str(budget) if budget else 'No budget specified'}"
            ],
            confidence=90 if zone_result.get('success') else 70
        )
        self._log_reflection(state, reflection)

        if self.trajectory_logger:
            self.trajectory_logger.log_agent_end(
                state.request_id,
                self.name,
                {
                    "zone": zone,
                    "weight": weight,
                    "rates_count": len(rates),
                    "has_recommendations": len(recommendations) > 0
                },
                duration_ms=(time.time() - start_time) * 1000
            )

        return AgentResponse(
            success=True,
            message=response_text,
            data={
                "zone": zone,
                "weight": weight,
                "rates": rates,
                "recommendations": recommendations,
                "trajectory": trajectory_steps
            },
            is_final=True,
            reflection=reflection
        )

    def _query_rates(
        self,
        zone: int,
        weight: float,
        urgency: str
    ) -> List[Dict[str, Any]]:
        """Query rate database for matching rates using Vanna."""
        # Database schema:
        # Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight,
        # FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver

        if self.vanna_client:
            try:
                # Round weight up to nearest whole number for lookup
                weight_lookup = int(weight) if weight == int(weight) else int(weight) + 1

                # Direct SQL query for the specific zone and weight
                sql = f"""
                SELECT Zone, Weight,
                       FedEx_First_Overnight,
                       FedEx_Priority_Overnight,
                       FedEx_Standard_Overnight,
                       FedEx_2Day_AM,
                       FedEx_2Day,
                       FedEx_Express_Saver
                FROM fedex_rates
                WHERE Zone = {zone}
                AND Weight = {weight_lookup}
                """
                logger.info(f"Querying database: Zone={zone}, Weight={weight_lookup}")

                results = self.vanna_client.run_sql(sql)

                if results is not None and len(results) > 0:
                    row = results.iloc[0]
                    logger.info(f"Found rates for Zone {zone}, Weight {weight_lookup}")

                    # Convert wide format to list of rate options
                    rates = []

                    service_info = {
                        'FedEx_First_Overnight': ('FedEx First Overnight', '1 business day by 8:00 AM'),
                        'FedEx_Priority_Overnight': ('FedEx Priority Overnight', '1 business day by 10:30 AM'),
                        'FedEx_Standard_Overnight': ('FedEx Standard Overnight', '1 business day by 3:00 PM'),
                        'FedEx_2Day_AM': ('FedEx 2Day AM', '2 business days by 10:30 AM'),
                        'FedEx_2Day': ('FedEx 2Day', '2 business days by 4:30 PM'),
                        'FedEx_Express_Saver': ('FedEx Express Saver', '3 business days by 4:30 PM'),
                    }

                    for col, (service_name, delivery_time) in service_info.items():
                        price = row.get(col)
                        if price is not None and price > 0:
                            rates.append({
                                'service': service_name,
                                'service_type': col,
                                'price_usd': float(price),
                                'delivery_time': delivery_time,
                                'zone': zone,
                                'weight_lb': weight_lookup
                            })

                    # Sort by price
                    rates.sort(key=lambda x: x['price_usd'])
                    logger.info(f"Returning {len(rates)} rate options")
                    return rates

            except Exception as e:
                logger.warning(f"Database query failed: {e}")

        # Return empty if no database connection
        logger.error("No database connection available - cannot provide accurate rates")
        return []

    def _get_static_rates(
        self,
        zone: int,
        weight: float,
        urgency: str
    ) -> List[Dict[str, Any]]:
        """Get static rate estimates."""
        # Base rates per zone (per lb)
        zone_rates = {
            2: {"overnight": 45, "2-day": 25, "standard": 15, "economy": 10},
            3: {"overnight": 50, "2-day": 30, "standard": 18, "economy": 12},
            4: {"overnight": 55, "2-day": 35, "standard": 22, "economy": 15},
            5: {"overnight": 60, "2-day": 40, "standard": 25, "economy": 18},
            6: {"overnight": 65, "2-day": 45, "standard": 28, "economy": 20},
            7: {"overnight": 70, "2-day": 50, "standard": 32, "economy": 22},
            8: {"overnight": 75, "2-day": 55, "standard": 35, "economy": 25},
        }

        base_rates = zone_rates.get(zone, zone_rates[5])

        # Calculate rates based on weight
        rates = []
        service_names = {
            "overnight": "FedEx Priority Overnight",
            "2-day": "FedEx 2Day",
            "standard": "FedEx Ground",
            "economy": "FedEx Home Delivery"
        }

        delivery_days = {
            "overnight": "1 business day",
            "2-day": "2 business days",
            "standard": "3-5 business days",
            "economy": "5-7 business days"
        }

        for service_type, base_rate in base_rates.items():
            # Weight-based pricing
            if weight <= 1:
                price = base_rate * 0.5
            elif weight <= 5:
                price = base_rate * 0.7
            elif weight <= 10:
                price = base_rate * 0.85
            elif weight <= 25:
                price = base_rate
            elif weight <= 50:
                price = base_rate * 1.5
            else:
                price = base_rate * 2.0

            rates.append({
                "service": service_names[service_type],
                "service_type": service_type,
                "price_usd": round(price, 2),
                "delivery_time": delivery_days[service_type],
                "zone": zone,
                "weight_lb": weight
            })

        return rates

    def _analyze_options(
        self,
        rates: List[Dict[str, Any]],
        budget: Optional[float],
        urgency: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze rate options and generate recommendations.

        IMPORTANT: User intent takes priority over cost optimization.
        If user asks for overnight, recommend overnight - don't override with cheapest.
        """
        recommendations = []

        if not rates:
            return recommendations

        # Sort by price
        sorted_rates = sorted(rates, key=lambda x: x['price_usd'])

        # Map urgency keywords to service types
        urgency_service_map = {
            'overnight': ['FedEx_First_Overnight', 'FedEx_Priority_Overnight', 'FedEx_Standard_Overnight'],
            'next-day': ['FedEx_First_Overnight', 'FedEx_Priority_Overnight', 'FedEx_Standard_Overnight'],
            'first': ['FedEx_First_Overnight'],
            'priority': ['FedEx_Priority_Overnight'],
            '2-day': ['FedEx_2Day_AM', 'FedEx_2Day'],
            '2day': ['FedEx_2Day_AM', 'FedEx_2Day'],
            'two-day': ['FedEx_2Day_AM', 'FedEx_2Day'],
            'express': ['FedEx_Express_Saver'],
            'saver': ['FedEx_Express_Saver'],
            '3-day': ['FedEx_Express_Saver'],
            'economy': ['FedEx_Express_Saver'],
            'cheapest': None,  # Will find cheapest
            'standard': None,  # No specific preference
        }

        # PRIMARY RECOMMENDATION: Based on user's expressed intent (urgency)
        if urgency and urgency.lower() not in ['standard', 'none', '']:
            urgency_lower = urgency.lower()
            target_services = urgency_service_map.get(urgency_lower)

            if target_services:
                # Find matching services
                matching_rates = [r for r in rates if r.get('service_type') in target_services]

                if matching_rates:
                    # Sort matching by price to get best value within user's preference
                    matching_sorted = sorted(matching_rates, key=lambda x: x['price_usd'])
                    best_match = matching_sorted[0]

                    recommendations.append({
                        "type": "user_intent",
                        "service": best_match['service'],
                        "price": best_match['price_usd'],
                        "delivery_time": best_match.get('delivery_time', ''),
                        "reason": f"Best {urgency} option as you requested - {best_match.get('delivery_time', '')}"
                    })

                    # If budget specified, check if it fits
                    if budget and best_match['price_usd'] > budget:
                        recommendations.append({
                            "type": "budget_warning",
                            "service": best_match['service'],
                            "price": best_match['price_usd'],
                            "reason": f"Note: {urgency} service costs ${best_match['price_usd']}, which exceeds your ${budget} budget"
                        })

        # SECONDARY: Show cheapest option (but not as primary if user had specific intent)
        if sorted_rates:
            cheapest = sorted_rates[0]
            rec_type = "recommended" if not urgency or urgency.lower() in ['standard', 'cheapest', 'none', ''] else "alternative"
            recommendations.append({
                "type": rec_type,
                "service": cheapest['service'],
                "price": cheapest['price_usd'],
                "delivery_time": cheapest.get('delivery_time', ''),
                "reason": f"Lowest price option at ${cheapest['price_usd']} ({cheapest.get('delivery_time', '')})"
            })

        # TERTIARY: Budget analysis if budget specified
        if budget:
            within_budget = [r for r in sorted_rates if r['price_usd'] <= budget]
            over_budget = [r for r in sorted_rates if r['price_usd'] > budget]

            if within_budget and not any(r['type'] == 'user_intent' for r in recommendations):
                # Only add budget recommendation if we didn't already have a user intent match
                best_in_budget = within_budget[0]
                if not any(r['service'] == best_in_budget['service'] for r in recommendations):
                    recommendations.append({
                        "type": "budget_fit",
                        "service": best_in_budget['service'],
                        "price": best_in_budget['price_usd'],
                        "delivery_time": best_in_budget.get('delivery_time', ''),
                        "reason": f"Best option within your ${budget} budget"
                    })
            elif not within_budget:
                recommendations.append({
                    "type": "over_budget",
                    "service": sorted_rates[0]['service'],
                    "price": sorted_rates[0]['price_usd'],
                    "reason": f"All options exceed your ${budget} budget. Cheapest is ${sorted_rates[0]['price_usd']}"
                })

        return recommendations

    def _analyze_budget_fit(
        self,
        rates: List[Dict[str, Any]],
        budget: float
    ) -> Dict[str, Any]:
        """Analyze how rates fit within budget."""
        within_budget = [r for r in rates if r['price_usd'] <= budget]
        over_budget = [r for r in rates if r['price_usd'] > budget]

        return {
            "budget": budget,
            "options_within_budget": len(within_budget),
            "options_over_budget": len(over_budget),
            "cheapest_option": min(r['price_usd'] for r in rates) if rates else None,
            "budget_sufficient": len(within_budget) > 0
        }

    def _generate_response(
        self,
        parsed: Dict[str, Any],
        zone_result: Dict[str, Any],
        weight: float,
        rates: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        budget: Optional[float]
    ) -> str:
        """Generate natural language response."""
        lines = []

        # Header
        lines.append(f"## Shipping Analysis: {parsed['origin']} to {parsed['destination']}")
        lines.append("")

        # Zone info
        lines.append(f"**Zone:** {zone_result['zone']} ({zone_result.get('reasoning', '')})")
        lines.append(f"**Package Weight:** {weight} lbs")
        if budget:
            lines.append(f"**Budget:** ${budget}")
        lines.append("")

        # Recommendations
        lines.append("### Recommendations")
        for rec in recommendations:
            emoji = "✅" if rec['type'] == 'budget_fit' else "📦"
            if rec['type'] == 'over_budget':
                emoji = "⚠️"
            lines.append(f"{emoji} **{rec['service']}**: ${rec['price']} - {rec['reason']}")
        lines.append("")

        # All options
        lines.append("### All Available Options")
        for rate in sorted(rates, key=lambda x: x['price_usd']):
            budget_marker = ""
            if budget:
                budget_marker = " ✅" if rate['price_usd'] <= budget else " ❌"
            lines.append(
                f"- **{rate['service']}**: ${rate['price_usd']}{budget_marker} "
                f"({rate['delivery_time']})"
            )

        return "\n".join(lines)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent system.

    Manages agent execution flow, state, and trajectory logging.
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        log_dir: str = "./logs",
        vanna_client: Any = None
    ):
        """Initialize the orchestrator with all agents."""
        self.trajectory_logger = TrajectoryLogger(
            log_dir=log_dir,
            console_enabled=True,
            file_enabled=True
        )

        agent_kwargs = {
            "llm_provider": llm_provider,
            "model": model,
            "api_key": api_key,
            "trajectory_logger": self.trajectory_logger
        }

        # Initialize agents
        self.supervisor = SupervisorAgent(**agent_kwargs)
        self.customer = CustomerInteractionAgent(**agent_kwargs)
        self.expert = ShippingExpertAgent(
            vanna_client=vanna_client,
            **agent_kwargs
        )

        self.agents = {
            AgentType.SUPERVISOR: self.supervisor,
            AgentType.CUSTOMER: self.customer,
            AgentType.EXPERT: self.expert
        }

        logger.info("AgentOrchestrator initialized with all agents")

    def process_query(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the agent system.

        Args:
            query: User's shipping query
            session_id: Optional session identifier

        Returns:
            Dictionary with response and trajectory
        """
        # Create session and request IDs
        session_id = session_id or str(uuid.uuid4())[:8]
        request_id = str(uuid.uuid4())[:8]

        # Initialize state
        state = AgentState(
            session_id=session_id,
            request_id=request_id,
            user_query=query
        )

        # Start trajectory
        trajectory = self.trajectory_logger.start_trajectory(
            session_id=session_id,
            request_id=request_id,
            user_query=query
        )

        # Process through agent chain
        current_agent_type = AgentType.SUPERVISOR
        final_response = None

        while current_agent_type is not None:
            agent = self.agents[current_agent_type]
            state.current_agent = current_agent_type

            try:
                response = agent.process(state)

                if response.reflection:
                    state.reflection[current_agent_type.value] = response.reflection

                if response.is_final:
                    final_response = response
                    break

                current_agent_type = response.next_agent

            except Exception as e:
                logger.error(f"Agent {current_agent_type.value} error: {e}")
                self.trajectory_logger.log_error(
                    request_id,
                    current_agent_type.value,
                    str(e)
                )
                final_response = AgentResponse(
                    success=False,
                    message=f"An error occurred: {str(e)}",
                    is_final=True
                )
                break

        # End trajectory
        final_result = {
            "response": final_response.message if final_response else "No response generated",
            "success": final_response.success if final_response else False,
            "data": final_response.data if final_response else None,
            "reflections": state.reflection
        }

        completed_trajectory = self.trajectory_logger.end_trajectory(
            request_id,
            final_result
        )

        return {
            "response": final_response.message if final_response else "No response generated",
            "success": final_response.success if final_response else False,
            "data": final_response.data if final_response else None,
            "trajectory": self.trajectory_logger.format_trajectory_markdown(completed_trajectory) if completed_trajectory else None,
            "reflections": state.reflection,
            "session_id": session_id,
            "request_id": request_id
        }


def create_shipping_agent_system(
    llm_provider: str = None,
    model: str = None,
    api_key: str = None,
    log_dir: str = "./logs",
    vanna_client: Any = None
) -> AgentOrchestrator:
    """
    Factory function to create the shipping agent system.

    Args:
        llm_provider: LLM provider ("openai" or "ollama")
        model: Model name
        api_key: API key for OpenAI
        log_dir: Directory for trajectory logs
        vanna_client: Optional Vanna client for SQL queries

    Returns:
        Configured AgentOrchestrator instance
    """
    # Use environment variables as defaults
    llm_provider = llm_provider or os.getenv("LLM_PROVIDER", "openai")
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = api_key or os.getenv("OPENAI_API_KEY")

    return AgentOrchestrator(
        llm_provider=llm_provider,
        model=model,
        api_key=api_key,
        log_dir=log_dir,
        vanna_client=vanna_client
    )

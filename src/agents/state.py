# =============================================================================
#  Filename: state.py
#
#  Short Description: State schema for LangGraph shipping workflow
#
#  Creation date: 2025-10-10
#  Author: Shrinivas Deshpande
# =============================================================================

"""
State Schema Module

Defines the shared state structure for the LangGraph multi-agent workflow.
All agents read from and write to this state during execution.
"""

from typing import TypedDict, Optional, Dict


class ShippingState(TypedDict):
    """
    Shared state schema for the LangGraph shipping workflow.
    
    This state is passed between all agents and accumulates information
    as the workflow progresses through different nodes.
    
    Attributes:
        # User Input Fields
        origin: Origin city and state (e.g., "Fremont, CA")
        destination: Destination city and state
        weight: Package weight in pounds
        budget: Maximum budget in USD
        urgency: Service urgency ("overnight"/"2-day"/"standard"/"economy")
        
        # Query Processing Fields
        user_question: Original natural language query
        sql_query: Generated SQL query string
        rate_results: Dictionary containing query results and metadata
        
        # Agent Reasoning Fields
        reflection: Self-reflection from reflection node
        recommendation: Shipping recommendation dictionary
        
        # Supervisor Fields
        supervisor_required: Boolean flag for supervisor escalation
        supervisor_decision: Supervisor's final decision dictionary
        
        # Metadata Fields
        illegal_item_flag: Flag for prohibited items
        error_message: Any error messages
        conversation_history: List of previous exchanges
    """
    
    # User inputs
    origin: str
    destination: str
    weight: float
    budget: float
    urgency: str
    
    # Query processing
    user_question: str
    sql_query: str
    rate_results: dict
    
    # Agent reasoning
    reflection: str
    reflection_chain_of_thought: str  # Detailed reasoning process
    recommendation: dict
    delivery_time: str  # Specific delivery time window
    
    # Supervisor
    supervisor_required: bool
    supervisor_decision: dict
    
    # Metadata
    illegal_item_flag: bool
    error_message: str
    conversation_history: list
    
    # Performance Timing (in milliseconds)
    timing: Dict[str, float]  # Tracks execution time for each step
    start_time: float  # Workflow start timestamp
    user_requested_reflection: bool  # True if user asks "is this right?" etc.
    
    # Interaction fields
    needs_clarification: bool  # True if missing required information
    clarification_message: str  # Message asking for clarification
    pre_query_message: str  # Friendly message before searching
    post_query_message: str  # Friendly message after results
    zone: int  # Internal FedEx zone (hidden from user)
    
    # Conversation context
    previous_recommendation: dict  # Last recommendation given to user
    is_follow_up_question: bool  # True if user is asking about previous response
    user_satisfaction: str  # "satisfied", "unsure", "dissatisfied"


def create_initial_state(user_question: str, request_supervisor: bool = False) -> ShippingState:
    """
    Create an initial state for the workflow.
    
    Args:
        user_question: User's natural language query
        request_supervisor: Whether supervisor review was explicitly requested
        
    Returns:
        Initialized ShippingState dictionary
    """
    import time
    from .validation_keywords import ValidationKeywords
    
    # Check if user is requesting reflection/verification
    user_wants_reflection = ValidationKeywords.is_reflection_request(user_question)
    
    return {
        "origin": "",
        "destination": "",
        "weight": None,
        "budget": None,
        "urgency": "standard",
        "user_question": user_question,
        "sql_query": "",
        "rate_results": {},
        "reflection": "",
        "reflection_chain_of_thought": "",
        "recommendation": {},
        "delivery_time": "",
        "supervisor_required": request_supervisor or ValidationKeywords.needs_supervisor(user_question),
        "supervisor_decision": {},
        "illegal_item_flag": False,
        "error_message": "",
        "conversation_history": [],
        "timing": {},
        "start_time": time.time() * 1000,  # Convert to milliseconds
        "user_requested_reflection": user_wants_reflection,
        "needs_clarification": False,
        "clarification_message": "",
        "pre_query_message": "",
        "post_query_message": "",
        "zone": 0,
        "previous_recommendation": {},
        "is_follow_up_question": False,
        "user_satisfaction": "unknown"
    }


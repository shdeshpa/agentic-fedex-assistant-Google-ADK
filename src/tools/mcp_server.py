"""
FastMCP Server for FedEx Shipping Assistant Tools.

Exposes zone calculation and weight estimation tools via MCP protocol.
"""

import os
from typing import Dict, Any
from fastmcp import FastMCP

from .zone_calculator import ZoneCalculator
from .weight_estimator import WeightEstimator

# Initialize FastMCP server
mcp = FastMCP(
    "FedEx Shipping Tools",
    instructions="""
    Tools for FedEx shipping rate calculations:
    - zone_calculator: Calculate shipping zone between origin and destination
    - weight_estimator: Estimate package weight based on item description
    """
)

# Initialize tool instances
_zone_calc = None
_weight_est = None


def _get_zone_calculator() -> ZoneCalculator:
    """Lazy initialization of ZoneCalculator."""
    global _zone_calc
    if _zone_calc is None:
        llm_provider = os.getenv("LLM_PROVIDER", "openai")
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        _zone_calc = ZoneCalculator(
            llm_provider=llm_provider,
            api_key=api_key,
            model=model
        )
    return _zone_calc


def _get_weight_estimator() -> WeightEstimator:
    """Lazy initialization of WeightEstimator."""
    global _weight_est
    if _weight_est is None:
        llm_provider = os.getenv("LLM_PROVIDER", "openai")
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        _weight_est = WeightEstimator(
            llm_provider=llm_provider,
            api_key=api_key,
            model=model
        )
    return _weight_est


@mcp.tool()
def zone_calculator(origin: str, destination: str) -> Dict[str, Any]:
    """
    Calculate shipping zone between origin and destination.

    Handles:
    - City names with typos (e.g., "San Fransisco" -> "San Francisco")
    - Airport codes (e.g., "SFO" -> "San Francisco, CA")
    - City nicknames (e.g., "Big Apple" -> "New York, NY")

    Args:
        origin: Origin location (city, state, airport code, or nickname)
        destination: Destination location (city, state, airport code, or nickname)

    Returns:
        Dictionary with:
        - zone: Shipping zone number (2-8)
        - origin: Resolved origin location
        - destination: Resolved destination location
        - reasoning: Explanation of zone calculation
        - trajectory: Step-by-step reasoning log
        - success: Whether calculation succeeded
    """
    calc = _get_zone_calculator()
    return calc.calculate_zone(origin, destination)


@mcp.tool()
def weight_estimator(item_description: str) -> Dict[str, Any]:
    """
    Estimate weight of an item based on description.

    Uses LLM-based reasoning to estimate weights of common items when
    users don't know exact package weights.

    Examples:
    - "wine bottle" -> ~3 lbs
    - "65 inch TV" -> ~55 lbs
    - "laptop with accessories" -> ~7 lbs

    Args:
        item_description: Description of the item(s) to ship

    Returns:
        Dictionary with:
        - weight_lbs: Estimated weight in pounds
        - weight_kg: Estimated weight in kilograms
        - confidence: Confidence level (high/medium/low)
        - confidence_percent: Confidence as percentage
        - reasoning: Explanation of estimation
        - trajectory: Step-by-step reasoning log
        - success: Whether estimation succeeded
    """
    est = _get_weight_estimator()
    return est.estimate_weight(item_description)


@mcp.tool()
def estimate_multiple_items(items: list) -> Dict[str, Any]:
    """
    Estimate total weight for multiple items.

    Args:
        items: List of item descriptions (strings) or dicts with:
            - description/item: Item description
            - quantity: Number of items (default: 1)

    Returns:
        Dictionary with:
        - total_weight_lbs: Total estimated weight in pounds
        - total_weight_kg: Total estimated weight in kilograms
        - items: List of individual item estimates
        - reasoning: Summary explanation
        - trajectory: Step-by-step reasoning log
        - success: Whether estimation succeeded
    """
    est = _get_weight_estimator()
    return est.estimate_multiple_items(items)


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()

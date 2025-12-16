"""
Weight Estimator Tool for FedEx Shipping Assistant.

Uses LLM to estimate weights of common items when users don't know exact weights.
"""

from typing import Dict, Any, Optional
import os
import json
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


class WeightEstimator:
    """
    Estimate package weights using LLM-based reasoning.

    Handles:
    - Common household items
    - Electronics (TVs, computers, etc.)
    - Food items (wine bottles, chocolates, etc.)
    - General descriptions
    """

    # Common item weight database (lbs) for quick lookup
    COMMON_WEIGHTS = {
        # Beverages
        'wine bottle': 3.0,
        'wine bottles': 3.0,  # per bottle
        'champagne bottle': 3.5,
        'beer case': 20.0,
        'beer 6-pack': 5.0,
        'water bottle': 1.0,
        'whiskey bottle': 3.0,

        # Electronics
        'laptop': 5.0,
        'macbook': 4.5,
        'ipad': 1.5,
        'iphone': 0.5,
        'playstation': 10.0,
        'xbox': 9.0,
        'nintendo switch': 2.0,

        # TVs by size
        '32 inch tv': 15.0,
        '32" tv': 15.0,
        '40 inch tv': 20.0,
        '40" tv': 20.0,
        '50 inch tv': 35.0,
        '50" tv': 35.0,
        '55 inch tv': 40.0,
        '55" tv': 40.0,
        '65 inch tv': 55.0,
        '65" tv': 55.0,
        '75 inch tv': 70.0,
        '75" tv': 70.0,
        '85 inch tv': 90.0,
        '85" tv': 90.0,

        # Food
        'chocolate box': 2.0,
        'chocolates': 2.0,
        'cookies': 1.5,
        'cake': 5.0,
        'gift basket': 8.0,
        'fruit basket': 10.0,

        # Clothing
        'shoes': 3.0,
        'pair of shoes': 3.0,
        'boots': 4.0,
        'jacket': 3.0,
        'coat': 5.0,
        'dress': 1.5,
        'suit': 4.0,

        # Books
        'book': 1.5,
        'textbook': 3.0,
        'hardcover book': 2.0,
        'paperback': 1.0,
        'box of books': 30.0,

        # Sporting goods
        'golf clubs': 30.0,
        'golf bag': 35.0,
        'bicycle': 30.0,
        'skateboard': 8.0,
        'snowboard': 15.0,
        'skis': 20.0,

        # Musical instruments
        'guitar': 10.0,
        'acoustic guitar': 10.0,
        'electric guitar': 12.0,
        'keyboard': 25.0,
        'violin': 5.0,

        # Furniture (small)
        'small table': 25.0,
        'chair': 20.0,
        'lamp': 8.0,
        'mirror': 15.0,
        'picture frame': 3.0,

        # Kitchen
        'blender': 8.0,
        'coffee maker': 10.0,
        'instant pot': 15.0,
        'air fryer': 12.0,
        'microwave': 30.0,
        'toaster': 5.0,
    }

    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize Weight Estimator.

        Args:
            llm_provider: "openai" or "ollama"
            api_key: OpenAI API key (required if llm_provider="openai")
            model: Model name for LLM
        """
        self.llm_provider = llm_provider

        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=model,
                temperature=0,
                api_key=api_key or os.getenv("OPENAI_API_KEY")
            )
        else:
            self.llm = ChatOllama(
                model=model,
                temperature=0
            )

        logger.info(f"WeightEstimator initialized with {llm_provider}")

    def estimate_weight(self, item_description: str) -> Dict[str, Any]:
        """
        Estimate weight of an item based on description.

        Args:
            item_description: Description of the item (e.g., "wine bottle", "65 inch TV")

        Returns:
            Dictionary with estimated weight, confidence, and reasoning
        """
        logger.info(f"Estimating weight for: {item_description}")

        trajectory = []
        item_lower = item_description.lower().strip()

        # Step 1: Check common weights database
        trajectory.append({
            "step": "check_database",
            "action": "Checking common weights database",
            "input": item_description
        })

        for key, weight in self.COMMON_WEIGHTS.items():
            if key in item_lower or item_lower in key:
                trajectory[-1]["output"] = f"Found: {weight} lbs"
                trajectory[-1]["reasoning"] = f"Matched '{item_description}' to '{key}' in database"

                return {
                    "weight_lbs": weight,
                    "weight_kg": round(weight * 0.453592, 2),
                    "confidence": "high",
                    "confidence_percent": 90,
                    "reasoning": f"'{item_description}' is typically around {weight} lbs based on common item database.",
                    "source": "database",
                    "trajectory": trajectory,
                    "success": True
                }

        trajectory[-1]["output"] = "Not found in database"
        trajectory[-1]["reasoning"] = "Item not in quick lookup database, using LLM estimation"

        # Step 2: Use LLM for estimation
        trajectory.append({
            "step": "llm_estimation",
            "action": "Using LLM to estimate weight",
            "input": item_description
        })

        weight, confidence, reasoning = self._estimate_with_llm(item_description)

        trajectory[-1]["output"] = f"{weight} lbs ({confidence} confidence)"
        trajectory[-1]["reasoning"] = reasoning

        return {
            "weight_lbs": weight,
            "weight_kg": round(weight * 0.453592, 2),
            "confidence": confidence,
            "confidence_percent": self._confidence_to_percent(confidence),
            "reasoning": reasoning,
            "source": "llm_estimation",
            "trajectory": trajectory,
            "success": True
        }

    def _estimate_with_llm(self, item_description: str) -> tuple:
        """
        Use LLM to estimate weight of an unknown item.

        Args:
            item_description: Item description

        Returns:
            Tuple of (weight_lbs, confidence, reasoning)
        """
        prompt = f"""You are a shipping expert. Estimate the weight of this item in pounds (lbs).

Item: "{item_description}"

Consider:
1. Standard product weights for this category
2. Packaging weight (add 10-20% for standard shipping box)
3. Common variations in size/model

Respond in this exact JSON format:
{{
    "weight_lbs": <number>,
    "confidence": "<high/medium/low>",
    "reasoning": "<brief explanation>"
}}

Examples:
- "laptop" -> {{"weight_lbs": 5.0, "confidence": "high", "reasoning": "Standard laptop weighs 4-6 lbs with packaging"}}
- "vintage vase" -> {{"weight_lbs": 8.0, "confidence": "medium", "reasoning": "Ceramic vases vary widely, estimating medium size with protective packaging"}}
- "handmade craft item" -> {{"weight_lbs": 3.0, "confidence": "low", "reasoning": "Handmade items vary significantly, using generic small package estimate"}}

Return ONLY the JSON, no additional text."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # Parse JSON response
            # Handle potential markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)

            weight = float(result.get("weight_lbs", 5.0))
            confidence = result.get("confidence", "medium").lower()
            reasoning = result.get("reasoning", "Estimated based on item description")

            return weight, confidence, reasoning

        except Exception as e:
            logger.warning(f"LLM weight estimation error: {e}")
            # Return default estimate
            return 5.0, "low", f"Unable to estimate precisely for '{item_description}', using default 5 lbs"

    def _confidence_to_percent(self, confidence: str) -> int:
        """Convert confidence level to percentage."""
        confidence_map = {
            "high": 85,
            "medium": 65,
            "low": 40
        }
        return confidence_map.get(confidence.lower(), 50)

    def estimate_multiple_items(self, items: list) -> Dict[str, Any]:
        """
        Estimate total weight for multiple items.

        Args:
            items: List of item descriptions or dicts with description and quantity

        Returns:
            Dictionary with total weight and individual item estimates
        """
        total_weight = 0.0
        item_estimates = []
        trajectory = []

        for item in items:
            # Handle both string and dict formats
            if isinstance(item, str):
                description = item
                quantity = 1
            else:
                description = item.get("description", item.get("item", ""))
                quantity = item.get("quantity", 1)

            estimate = self.estimate_weight(description)
            item_weight = estimate["weight_lbs"] * quantity
            total_weight += item_weight

            item_estimates.append({
                "item": description,
                "quantity": quantity,
                "unit_weight_lbs": estimate["weight_lbs"],
                "total_weight_lbs": item_weight,
                "confidence": estimate["confidence"]
            })

            trajectory.extend(estimate["trajectory"])

        return {
            "total_weight_lbs": round(total_weight, 2),
            "total_weight_kg": round(total_weight * 0.453592, 2),
            "items": item_estimates,
            "reasoning": f"Total estimated weight for {len(items)} item(s): {round(total_weight, 2)} lbs",
            "trajectory": trajectory,
            "success": True
        }

# =============================================================================
#  Filename: __init__.py
#
#  Short Description: Agents package initialization
#
#  Creation date: 2025-10-10
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Agents Package - Multi-Agent FedEx Shipping System

This package provides a multi-agent system for intelligent FedEx shipping
rate queries and recommendations using Google ADK and specialized MCP tools.

Modules:
- adk_agents: Google ADK-based multi-agent orchestration
- unified_agent: Legacy single agent (deprecated)
- zone_lookup_tool: Zone lookup with typo correction
- validation_keywords: Centralized validation keyword management
- state: State management for the system
"""

# Legacy imports (kept for backward compatibility)
from .unified_agent import UnifiedFedExAgent
from .zone_lookup_tool import FedExZoneLookupTool
from .validation_keywords import ValidationKeywords
from .state import ShippingState, create_initial_state

# New ADK-based agents
from .adk_agents import (
    AgentOrchestrator,
    create_shipping_agent_system
)

__version__ = "3.0.0"
__author__ = "Shrinivas Deshpande"

__all__ = [
    # New multi-agent system
    'AgentOrchestrator',
    'create_shipping_agent_system',
    # Legacy (deprecated)
    'UnifiedFedExAgent',
    'FedExZoneLookupTool',
    'ValidationKeywords',
    'ShippingState',
    'create_initial_state'
]
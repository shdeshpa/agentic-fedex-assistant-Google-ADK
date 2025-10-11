# =============================================================================
#  Filename: __init__.py
#
#  Short Description: Agents package initialization
#
#  Creation date: 2025-10-10
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Agents Package - Unified FedEx Agent System

This package provides a unified agent system for intelligent FedEx shipping
rate queries and recommendations using specialized tools.

Modules:
- unified_agent: Single agent with multiple specialized tools
- zone_lookup_tool: Zone lookup with typo correction
- validation_keywords: Centralized validation keyword management
- state: State management for the system
"""

from .unified_agent import UnifiedFedExAgent
from .zone_lookup_tool import FedExZoneLookupTool
from .validation_keywords import ValidationKeywords
from .state import ShippingState, create_initial_state

__version__ = "2.0.0"
__author__ = "Asif Qamar"

__all__ = [
    'UnifiedFedExAgent',
    'FedExZoneLookupTool',
    'ValidationKeywords',
    'ShippingState',
    'create_initial_state'
]
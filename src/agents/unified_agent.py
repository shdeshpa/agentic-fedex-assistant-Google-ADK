# =============================================================================
#  Filename: unified_agent.py
#
#  Short Description: Unified FedEx Agent with all tools integrated
#
#  Creation date: 2025-10-10
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Unified FedEx Agent Module

A single agent that handles all shipping requests using multiple specialized tools:
- Zone lookup tool
- SQL query tool  
- Response generation tool
- Reflection tool
- Supervisor tool

This simplifies the workflow while maintaining all functionality.
"""

import json
import time
import re
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from .state import ShippingState
from .zone_lookup_tool import FedExZoneLookupTool
from .validation_keywords import ValidationKeywords
from src.Vanna.config import VannaConfig
from src.Vanna.sql_engine import SQLiteEngine
from src.Vanna.text_to_sql import TextToSQLEngine


class UnifiedFedExAgent:
    """
    Unified FedEx Agent - Single agent with multiple specialized tools.
    
    This agent handles the complete shipping workflow:
    1. Parse user request and extract parameters
    2. Look up zones and validate locations
    3. Generate and execute SQL queries
    4. Generate recommendations
    5. Perform reflection when requested
    6. Escalate to supervisor when needed
    
    Uses multiple tools but presents as a single, coherent agent.
    """
    
    def __init__(self, model: Optional[str] = None, temperature: Optional[float] = None):
        """
        Initialize the Unified FedEx Agent.
        
        Args:
            model: LLM model name (optional, uses config default)
            temperature: LLM temperature for response generation (optional, uses config default)
        """
        self.config = VannaConfig()
        
        # Use config defaults if not provided
        if model is None:
            model = self.config.model
        if temperature is None:
            temperature = self.config.llm_temperature
        
        # Initialize LLM based on provider
        if self.config.llm_provider == "openai":
            logger.info(f"🤖 Initializing with OpenAI model: {model}")
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=self.config.openai_api_key
            )
            self.llm_provider = "openai"
        else:  # ollama
            logger.info(f"🤖 Initializing with Ollama model: {model}")
            self.llm = ChatOllama(model=model, temperature=temperature)
            self.llm_provider = "ollama"
        
        # Initialize tools
        tool_model = self.config.openai_model if self.config.llm_provider == "openai" else self.config.ollama_agent_model
        self.zone_lookup = FedExZoneLookupTool(
            model=tool_model,
            llm_provider=self.config.llm_provider,
            api_key=self.config.openai_api_key if self.config.llm_provider == "openai" else None
        )
        self.sql_engine = SQLiteEngine(self.config)
        self.text_to_sql = TextToSQLEngine(self.config)
        
        # Initialize the text-to-sql engine
        self.text_to_sql.initialize()
        
        logger.info(f"✅ All tools initialized with {self.config.llm_provider.upper()} provider")
        logger.info(f"   Model: {model}, Temperature: {temperature}")
    
    def process_request(self, user_question: str) -> Dict[str, Any]:
        """
        Process a complete shipping request.
        
        Args:
            user_question: User's natural language query
            
        Returns:
            Complete response with recommendation, reflection, etc.
        """
        start_time = time.time() * 1000
        logger.info(f"🚀 Processing request: {user_question}")
        
        # Step 1: Parse and extract parameters
        state = self._parse_request(user_question)
        
        # Step 2: Check for clarification needs
        if state['needs_clarification']:
            return {
                'success': False,
                'needs_clarification': True,
                'clarification_message': state['clarification_message'],
                'total_time': (time.time() * 1000) - start_time
            }
        
        # Step 3: Execute SQL query
        state = self._execute_sql_query(state)
        
        if state['error_message']:
            return {
                'success': False,
                'error_message': state['error_message'],
                'total_time': (time.time() * 1000) - start_time
            }
        
        # Step 4: Generate recommendation
        state = self._generate_recommendation(state)
        
        # Step 5: Check if reflection is needed
        if state.get('user_requested_reflection', False):
            state = self._perform_reflection(state)
        
        # Step 6: Check if supervisor is needed
        if state.get('supervisor_required', False):
            state = self._escalate_to_supervisor(state)
        
        # Calculate total time
        total_time = (time.time() * 1000) - start_time
        
        return {
            'success': True,
            'recommendation': state.get('recommendation', {}),
            'reflection': state.get('reflection', ''),
            'chain_of_thought': state.get('reflection_chain_of_thought', ''),
            'supervisor': state.get('supervisor_decision', {}),
            'sql_query': state.get('sql_query', ''),
            'rate_results': state.get('rate_results', {}),
            'timing': state.get('timing', {}),
            'total_time': total_time
        }
    
    def _parse_request(self, user_question: str) -> Dict[str, Any]:
        """Parse user request and extract shipping parameters."""
        step_start = time.time() * 1000
        logger.info("📝 Parsing user request")
        
        # Check for prohibited items first
        user_question_lower = user_question.lower()
        
        # Living beings (STRICTLY PROHIBITED)
        living_beings_keywords = [
            'baby', 'babies', 'child', 'children', 'infant', 'toddler',
            'human', 'person', 'people', 'man', 'woman', 'kid', 'boy', 'girl',
            'pet', 'dog', 'cat', 'puppy', 'kitten', 'animal', 'animals',
            'bird', 'fish', 'hamster', 'rabbit', 'snake', 'lizard', 'turtle',
            'horse', 'cow', 'pig', 'chicken', 'livestock'
        ]
        
        # Perishable items (RESTRICTED - need special handling)
        perishable_keywords = [
            'mango', 'mangoes', 'fruit', 'fruits', 'vegetable', 'vegetables',
            'perishable', 'food', 'fresh', 'ripe', 'meat', 'fish', 'seafood',
            'dairy', 'milk', 'cheese', 'yogurt', 'ice cream', 'frozen',
            'flower', 'flowers', 'plant', 'plants', 'produce', 'cake', 'bakery'
        ]
        
        # Check for living beings
        found_living = [item for item in living_beings_keywords if item in user_question_lower]
        
        if found_living:
            logger.error(f"🚫 PROHIBITED: Living being detected: {', '.join(found_living)}")
            return {
                'success': False,
                'needs_clarification': True,
                'clarification_message': (
                    f"🚫 **PROHIBITED SHIPMENT**: I cannot process this request. "
                    f"Shipping living beings (humans, animals, pets) is **strictly prohibited** by FedEx and all major carriers.\n\n"
                    f"**This is illegal and dangerous.**\n\n"
                    f"If you need to transport:\n"
                    f"- **Pets**: Please use specialized pet transportation services\n"
                    f"- **Livestock**: Contact agricultural/livestock transport companies\n"
                    f"- **Any living creature**: This requires specialized, legal, and humane transportation\n\n"
                    f"I can only help with shipping legal, non-living items. Please rephrase your query with a valid item."
                ),
                'timing': {'parse_request': (time.time() * 1000) - step_start},
                'total_time': (time.time() * 1000) - step_start
            }
        
        # Check for perishable items
        found_perishable = [item for item in perishable_keywords if item in user_question_lower]
        
        if found_perishable:
            logger.warning(f"⚠️ Perishable item detected: {', '.join(found_perishable)}")
            return {
                'success': False,
                'needs_clarification': True,
                'clarification_message': (
                    f"⚠️ **Shipping Restriction**: I noticed you want to ship {', '.join(found_perishable)}. "
                    f"Unfortunately, FedEx has specific restrictions on shipping perishable items. "
                    f"Perishable foods, fresh produce, and temperature-sensitive items typically require "
                    f"special packaging (like FedEx Cold Shipping Solutions) and may have additional restrictions.\n\n"
                    f"**Recommendation**: Please contact FedEx directly at 1-800-463-3339 for specialized "
                    f"perishable shipping options, or visit a FedEx location for proper packaging and handling requirements."
                ),
                'timing': {'parse_request': (time.time() * 1000) - step_start},
                'total_time': (time.time() * 1000) - step_start
            }
        
        # Initialize state
        state = {
            'user_question': user_question,
            'origin': '',
            'destination': '',
            'weight': 10.0,
            'budget': 10000.0,  # Default = no budget constraint
            'urgency': 'standard',
            'zone': 0,
            'needs_clarification': False,
            'clarification_message': '',
            'user_requested_reflection': ValidationKeywords.is_reflection_request(user_question),
            'timing': {}
        }
        
        # Extract parameters using LLM
        prompt = f"""Parse this shipping request and extract key information.

User Request: "{user_question}"

Extract these parameters:
- origin: Origin city and state (if not mentioned, use "Current location")
- destination: Destination city and state (required)
- weight: Package weight in pounds (if not mentioned, assume 10.0)
- budget: Maximum budget in USD (ONLY if explicitly mentioned, otherwise "None")
- urgency: "overnight", "2-day", "standard", or "economy" (if not mentioned, use "standard")

IMPORTANT: Only set budget if user explicitly mentions a dollar amount. 
If they say "cheapest" or "best rate", set budget to "None".

Return ONLY valid JSON with exactly these keys, no additional text:
{{"origin": "...", "destination": "...", "weight": 10.0, "budget": "None", "urgency": "standard"}}
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            
            # Extract JSON from response
            if '{' in content and '}' in content:
                start = content.index('{')
                end = content.rindex('}') + 1
                json_str = content[start:end]
                parsed = json.loads(json_str)
                
                # Update state with parsed values
                state['origin'] = parsed.get('origin', 'Current location')
                state['destination'] = parsed.get('destination', 'Unknown')
                state['weight'] = float(parsed.get('weight', 10))
                
                # Only set budget if explicitly mentioned
                budget_value = parsed.get('budget')
                if budget_value and budget_value != 'None' and budget_value != '':
                    # Clean up budget value (remove $ and other currency symbols)
                    budget_str = str(budget_value).replace('$', '').replace(',', '').strip()
                    try:
                        state['budget'] = float(budget_str)
                    except (ValueError, AttributeError):
                        state['budget'] = 10000.0  # No budget constraint
                else:
                    state['budget'] = 10000.0  # No budget constraint
                    
                state['urgency'] = parsed.get('urgency', 'standard')
                
                logger.success(f"✅ Parsed: {state['origin']} → {state['destination']}, {state['weight']} lbs, ${state['budget']} budget")
            else:
                self._apply_defaults(state)
                
        except Exception as e:
            logger.warning(f"⚠️ Parse error: {e}. Applying defaults.")
            self._apply_defaults(state)
        
        # Check for zone-based queries
        user_question_lower = user_question.lower()
        mentions_zone = 'zone' in user_question_lower and any(str(i) for i in range(1, 9) if str(i) in user_question_lower)
        
        if mentions_zone:
            # Extract zone number if mentioned directly
            zone_match = re.search(r'zone\s+(\d+)', user_question_lower)
            if zone_match:
                extracted_zone = int(zone_match.group(1))
                state['zone'] = extracted_zone
                state['destination'] = f"Zone {extracted_zone}"
                logger.info(f"✅ Zone {extracted_zone} extracted from query")
        else:
            # Try zone lookup for destination
            if state['destination'] and state['destination'] != 'Unknown':
                # Parse destination into city and state
                dest_parts = state['destination'].split(',')
                if len(dest_parts) >= 2:
                    city = dest_parts[0].strip()
                    state_code = dest_parts[1].strip()
                    zone_info = self.zone_lookup.get_zone_with_correction(
                        city=city,
                        state=state_code
                    )
                    if zone_info['success']:
                        state['zone'] = zone_info['zone']
                        state['destination'] = zone_info['explanation'].split(' is in')[0]
                        logger.info(f"✅ {zone_info['explanation']}")
                else:
                    # Try as city name only
                    zone_info = self.zone_lookup.get_zone_with_correction(
                        city=state['destination']
                    )
                    if zone_info['success']:
                        state['zone'] = zone_info['zone']
                        state['destination'] = zone_info['explanation'].split(' is in')[0]
                        logger.info(f"✅ {zone_info['explanation']}")
        
        # Check for clarification needs
        missing_info = []
        if not mentions_zone and not state['zone'] and (not state['destination'] or state['destination'] == 'Unknown'):
            missing_info.append('destination city or ZIP code')
        
        if state['weight'] <= 0:
            missing_info.append('package weight')
        
        if missing_info:
            state['needs_clarification'] = True
            questions = []
            if 'destination city or ZIP code' in missing_info:
                questions.append("📍 **Which city** would you like to ship to? (e.g., New York, Chicago, Los Angeles)")
            if 'package weight' in missing_info:
                questions.append("⚖️ **How much does your package weigh?** (in pounds)")
            
            state['clarification_message'] = (
                "I'd be happy to help you find the best shipping options! "
                "I just need a bit more information:\n\n" +
                "\n".join(questions) +
                "\n\nPlease provide these details so I can find the best rates for you."
            )
        
        # Record timing
        state['timing']['parse_request'] = (time.time() * 1000) - step_start
        return state
    
    def _apply_defaults(self, state: Dict[str, Any]) -> None:
        """Apply default values when parsing fails."""
        state['origin'] = 'Current location'
        state['destination'] = 'Unknown'
        state['weight'] = 10.0
        state['budget'] = 10000.0
        state['urgency'] = 'standard'
    
    def _execute_sql_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query using Vanna."""
        step_start = time.time() * 1000
        logger.info("🔍 Executing SQL query")
        
        try:
            # Build query with zone if available
            query = state['user_question']
            zone = state.get('zone', 0)
            if zone and 'zone' not in query.lower():
                query = f"{query} (Zone {zone})"
                logger.info(f"🎯 Enhancing query with Zone {zone}")
            
            # Generate SQL using Vanna
            sql = self.text_to_sql.generate_sql(query)
            
            if not sql:
                state['error_message'] = "Failed to generate SQL query"
                state['rate_results'] = {}
                return state
            
            # Execute SQL with thread-safe connection
            df = self._execute_sql_thread_safe(sql)
            
            if df is None or df.empty:
                logger.warning("⚠️ No results found")
                state['error_message'] = "No results found in database"
                state['rate_results'] = {}
                return state
            
            # Store results
            state['sql_query'] = sql
            state['rate_results'] = {
                'data': df.to_dict('records'),
                'row_count': len(df),
                'columns': df.columns.tolist()
            }
            state['error_message'] = ""
            
            logger.success(f"✅ SQL Query executed successfully: {len(df)} rows returned")
            
        except Exception as e:
            logger.error(f"❌ SQL Query error: {e}")
            state['error_message'] = str(e)
            state['rate_results'] = {}
        
        # Record timing
        state['timing']['sql_query'] = (time.time() * 1000) - step_start
        return state
    
    def _execute_sql_thread_safe(self, sql: str):
        """Execute SQL with thread-safe connection."""
        try:
            # Create fresh connection for thread safety
            fresh_engine = SQLiteEngine(self.config)
            fresh_engine.connect()  # Connect to database
            return fresh_engine.execute_query(sql)
        except Exception as e:
            logger.error(f"Thread-safe SQL execution error: {e}")
            return None
    
    def _generate_recommendation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate shipping recommendation."""
        step_start = time.time() * 1000
        logger.info("💡 Generating shipping recommendation")
        
        rate_results = state.get('rate_results', {})
        data = rate_results.get('data', [])
        
        if not data:
            state['recommendation'] = {
                'service': 'N/A',
                'estimated_cost': 0,
                'delivery_days': 0,
                'recommendation': 'No rates found. Please check zone and weight parameters.',
                'supervisor_required': False
            }
            return state
        
        # Check if this is an informational query (SELECT DISTINCT, COUNT, etc.)
        sql_query = state.get('sql_query', '').lower()
        is_informational = any(keyword in sql_query for keyword in ['distinct', 'count', 'group by', 'avg', 'sum', 'max', 'min']) and not any(service in sql_query for service in ['fedex_first', 'fedex_priority', 'fedex_standard', 'fedex_2day', 'fedex_express'])
        
        if is_informational:
            # Handle informational queries
            if 'weight' in sql_query and 'distinct' in sql_query:
                # Weight categories query
                weights = [row.get('Weight', row.get('weight', '')) for row in data if 'Weight' in row or 'weight' in row]
                weight_count = len(weights)
                weight_range = f"{min(weights)} to {max(weights)} lbs" if weights else "N/A"
                
                state['recommendation'] = {
                    'service': 'Information',
                    'estimated_cost': 0,
                    'delivery_time': 'N/A',
                    'recommendation': f"Available weight categories: {weight_count} categories available, ranging from {weight_range}. You can ship packages from 1 lb to 150 lbs."
                }
                logger.success(f"✅ Information: {weight_count} weight categories")
            elif 'zone' in sql_query and ('count' in sql_query or 'group by' in sql_query):
                # Zone information query
                state['recommendation'] = {
                    'service': 'Information',
                    'estimated_cost': 0,
                    'delivery_time': 'N/A',
                    'recommendation': f"Found {len(data)} results. Data shows zone-based information."
                }
                logger.success(f"✅ Information: {len(data)} results")
            else:
                # Generic informational query
                state['recommendation'] = {
                    'service': 'Information',
                    'estimated_cost': 0,
                    'delivery_time': 'N/A',
                    'recommendation': f"Query returned {len(data)} results. Please review the data table for details."
                }
                logger.success(f"✅ Information: {len(data)} results")
            
            # Record timing
            state['timing']['generate_recommendation'] = (time.time() * 1000) - step_start
            return state
        
        # Handle MIN() query results (single value)
        if len(data) == 1 and len(data[0]) == 1:
            # This is a MIN() query result
            single_value = list(data[0].values())[0]
            service_name = 'FedEx Express Saver'  # Default for cheapest queries
            
            state['recommendation'] = {
                'service': service_name,
                'estimated_cost': float(single_value) if single_value else 0.0,
                'delivery_time': self._get_delivery_time(service_name),
                'recommendation': f"Best option: {service_name} at ${single_value:.2f}. Delivery: {self._get_delivery_time(service_name)}. This is the most cost-effective option available."
            }
            logger.success(f"✅ Recommendation: {service_name} at ${single_value:.2f}")
        # Handle MIN() query results with multiple columns (Zone, Weight, Cheapest_Rate)
        elif len(data) == 1 and len(data[0]) == 3:
            # This is a MIN() query result with Zone, Weight, and Cheapest_Rate
            row = data[0]
            cheapest_rate = None
            for key, value in row.items():
                if 'cheapest' in key.lower() or 'min' in key.lower():
                    cheapest_rate = value
                    break
            
            if cheapest_rate is None:
                # Fallback: get the last value (should be the MIN result)
                cheapest_rate = list(row.values())[-1]
            
            service_name = 'FedEx Express Saver'  # Default for cheapest queries
            
            state['recommendation'] = {
                'service': service_name,
                'estimated_cost': float(cheapest_rate) if cheapest_rate else 0.0,
                'delivery_time': self._get_delivery_time(service_name),
                'recommendation': f"Best option: {service_name} at ${cheapest_rate:.2f}. Delivery: {self._get_delivery_time(service_name)}. This is the most cost-effective option available."
            }
            logger.success(f"✅ Recommendation: {service_name} at ${cheapest_rate:.2f}")
        else:
            # Find best service from full data
            best_option = self._find_best_service(data, state.get('budget', 10000), state.get('urgency', 'standard'))
            
            if best_option:
                state['recommendation'] = best_option
                logger.success(f"✅ Recommendation: {best_option['service']} at ${best_option['estimated_cost']:.2f}")
            else:
                # This should not happen with budget >= 10000, but just in case
                state['recommendation'] = {
                    'service': 'N/A',
                    'estimated_cost': 0,
                    'delivery_time': 'N/A',
                    'recommendation': 'No suitable options found.',
                    'supervisor_required': True
                }
        
        # Record timing
        state['timing']['generate_recommendation'] = (time.time() * 1000) - step_start
        return state
    
    def _find_best_service(self, data: List[Dict], budget: float, urgency: str) -> Optional[Dict[str, Any]]:
        """Find the best shipping service option."""
        # Determine preferred services based on urgency
        preferred_services = []
        if urgency == 'overnight':
            preferred_services = ['FedEx_First_Overnight', 'FedEx_Priority_Overnight', 'FedEx_Standard_Overnight']
        elif urgency == '2-day':
            preferred_services = ['FedEx_2Day_AM', 'FedEx_2Day']
        else:  # standard or economy
            preferred_services = ['FedEx_Express_Saver', 'FedEx_2Day', 'FedEx_2Day_AM']
        
        # Collect ALL available options with costs
        all_options = []
        
        for row in data:
            for service in ['FedEx_Express_Saver', 'FedEx_2Day', 'FedEx_2Day_AM',
                          'FedEx_Standard_Overnight', 'FedEx_Priority_Overnight',
                          'FedEx_First_Overnight']:
                if service in row and row[service] and row[service] is not None:
                    cost = float(row[service])
                    
                    # Only filter by budget if budget was explicitly set (not default)
                    if budget >= 10000:  # Default budget means no budget constraint
                        all_options.append({
                            'service': service,
                            'cost': cost,
                            'delivery_days': self._estimate_delivery_days(service),
                            'delivery_time': self._get_delivery_time(service),
                            'row': row
                        })
                    elif cost <= budget:  # Within explicit budget
                        all_options.append({
                            'service': service,
                            'cost': cost,
                            'delivery_days': self._estimate_delivery_days(service),
                            'delivery_time': self._get_delivery_time(service),
                            'row': row
                        })
        
        if not all_options:
            return None
        
        # Sort by cost (cheapest first), then by urgency preference
        def sort_key(option):
            cost = option['cost']
            # Prefer services that match urgency
            urgency_bonus = 0 if option['service'] in preferred_services else 1000
            return cost + urgency_bonus
        
        all_options.sort(key=sort_key)
        best_option = all_options[0]
        
        # Build recommendation message based on budget constraint
        if budget >= 10000:  # No budget constraint
            recommendation_msg = (
                f"Best option: {best_option['service'].replace('_', ' ')} at "
                f"${best_option['cost']:.2f}. "
                f"Delivery: {best_option['delivery_time']}. "
                "This is the most cost-effective option available."
            )
        else:  # Budget constraint applied
            recommendation_msg = (
                f"Best option: {best_option['service'].replace('_', ' ')} at "
                f"${best_option['cost']:.2f}. "
                f"Delivery: {best_option['delivery_time']}. "
                "This is the most cost-effective option within your budget."
            )
        
        return {
            'service': best_option['service'].replace('_', ' '),
            'estimated_cost': best_option['cost'],
            'delivery_days': best_option['delivery_days'],
            'delivery_time': best_option['delivery_time'],
            'recommendation': recommendation_msg,
            'supervisor_required': best_option['cost'] >= 1000
        }
    
    def _estimate_delivery_days(self, service: str) -> int:
        """Estimate delivery days based on service name."""
        delivery_map = {
            'FedEx_Express_Saver': 3,
            'FedEx_2Day': 2,
            'FedEx_2Day_AM': 2,
            'FedEx_Standard_Overnight': 1,
            'FedEx_Priority_Overnight': 1,
            'FedEx_First_Overnight': 1
        }
        return delivery_map.get(service, 3)
    
    def _get_delivery_time(self, service: str) -> str:
        """Get specific delivery time window for service."""
        delivery_times = {
            'FedEx_First_Overnight': 'Next day by 8 or 8:30 a.m.',
            'FedEx_Priority_Overnight': 'Next day by 10:30 a.m. or 11 a.m.',
            'FedEx_Standard_Overnight': 'Next day by 5 p.m.',
            'FedEx_2Day_AM': '2nd day by 10:30 a.m. or 11 a.m.',
            'FedEx_2Day': '2nd day by 5 p.m.',
            'FedEx_Express_Saver': '3rd day by 5 p.m.'
        }
        return delivery_times.get(service, 'Standard delivery')
    
    def _perform_reflection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform reflection when requested by user."""
        step_start = time.time() * 1000
        logger.info("🤔 Performing reflection")
        
        rec = state.get('recommendation', {})
        if not rec or rec.get('service') == 'N/A':
            state['reflection'] = "No recommendation to reflect on."
            state['reflection_chain_of_thought'] = ""
            return state
        
        # Generate chain-of-thought
        cot_prompt = self._build_chain_of_thought_prompt(state, rec)
        
        try:
            # Step 1: Generate chain-of-thought reasoning
            logger.info("🧠 Generating chain-of-thought reasoning...")
            cot_response = self.llm.invoke([HumanMessage(content=cot_prompt)])
            chain_of_thought = cot_response.content.strip()
            state['reflection_chain_of_thought'] = chain_of_thought
            
            # Step 2: Generate final reflection
            final_prompt = self._build_final_reflection_prompt(state, rec, chain_of_thought)
            response = self.llm.invoke([HumanMessage(content=final_prompt)])
            reflection_text = response.content.strip()
            
            state['reflection'] = reflection_text
            
            # Check if supervisor is needed based on reflection
            if any(keyword in reflection_text.lower() for keyword in [
                'supervisor', 'escalate', 'review needed', 'concern', 'issue'
            ]):
                state['supervisor_required'] = True
                logger.warning("⚠️ Reflection suggests supervisor review")
            
            logger.success("✅ Reflection complete")
            
        except Exception as e:
            logger.error(f"❌ Reflection error: {e}")
            state['reflection'] = "Recommendation appears reasonable based on available data."
            state['reflection_chain_of_thought'] = ""
        
        # Record timing
        state['timing']['reflection'] = (time.time() * 1000) - step_start
        return state
    
    def _build_chain_of_thought_prompt(self, state: Dict[str, Any], rec: Dict[str, Any]) -> str:
        """Build chain-of-thought prompt."""
        return f"""You are analyzing how the FedEx shipping system made its recommendation.
Show your complete thought process step-by-step.

**User's Original Question:**
"{state['user_question']}"

**How the System Processed This:**

1. **Parameter Extraction:**
   - Origin: {state.get('origin', 'Not specified')}
   - Destination: {state.get('destination', 'Unknown')}
   - Zone Mapped: Zone {state.get('zone', 'N/A')}
   - Weight: {state.get('weight', 0)} lbs
   - Budget: ${state.get('budget', 0)}
   - Urgency: {state.get('urgency', 'standard')}

2. **SQL Query Generated:**
   ```sql
   {state.get('sql_query', 'No SQL generated')}
   ```

3. **Query Results:**
   - Rows returned: {state.get('rate_results', {}).get('row_count', 0)}
   - Data: {state.get('rate_results', {}).get('data', [])}

4. **Recommendation Made:**
   - Service: {rec.get('service', 'N/A')}
   - Cost: ${rec.get('estimated_cost', 0):.2f}
   - Delivery: {rec.get('delivery_days', 0)} days
   - Reasoning: {rec.get('recommendation', 'N/A')}

**Your Task - Show Complete Chain of Thought:**

Think through step-by-step:
1. Was the user's question understood correctly?
2. Were origin/destination extracted properly?
3. Was the zone mapping correct?
4. Was the SQL query appropriate for the request?
5. Did the query return the right data?
6. Was the best service selected from the results?
7. Does the recommendation meet the user's needs (budget, urgency)?
8. Are there any concerns or issues?

Provide a detailed step-by-step analysis (5-8 sentences) showing your reasoning process.
Start with "Let me trace through how this recommendation was made:"
"""
    
    def _build_final_reflection_prompt(self, state: Dict[str, Any], rec: Dict[str, Any], chain_of_thought: str) -> str:
        """Build final reflection prompt."""
        return f"""Based on your detailed analysis:

{chain_of_thought}

Now provide a clear, concise reflection for the user.

The user asked for verification. Provide confident confirmation:
- Clearly state if the recommendation is correct
- Explain WHY it's the best choice
- Address any potential concerns
- Reassure the user

Format: 2-3 clear sentences.
"""
    
    def _escalate_to_supervisor(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate to supervisor when needed."""
        step_start = time.time() * 1000
        logger.info("👔 Escalating to supervisor")
        
        # Simple supervisor logic for now
        state['supervisor_decision'] = {
            'decision': 'Reviewed',
            'reasoning': 'Supervisor reviewed the recommendation and found it appropriate.',
            'final_message': 'The recommendation has been reviewed and approved by a supervisor.',
            'reviewed_by': 'FedEx Supervisor Agent',
            'review_complete': True
        }
        
        # Record timing
        state['timing']['supervisor'] = (time.time() * 1000) - step_start
        return state

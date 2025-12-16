"""
Zone Calculator Tool for FedEx Shipping Assistant.

Handles:
- City names with typos (LLM-based correction)
- Airport codes (SFO, LAX, JFK, etc.)
- City nicknames (Big Apple, Windy City, etc.)
"""

from typing import Optional, Tuple, Dict, Any
import os
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


class ZoneCalculator:
    """
    Calculate shipping zones with intelligent location resolution.

    Features:
    - Airport code recognition (SFO -> San Francisco, CA)
    - City nickname handling (Big Apple -> New York, NY)
    - Typo correction via LLM
    - Zone calculation based on origin/destination
    """

    # Airport code to city mapping
    AIRPORT_CODES = {
        'SFO': ('San Francisco', 'CA'),
        'LAX': ('Los Angeles', 'CA'),
        'SAN': ('San Diego', 'CA'),
        'OAK': ('Oakland', 'CA'),
        'SJC': ('San Jose', 'CA'),
        'JFK': ('New York', 'NY'),
        'LGA': ('New York', 'NY'),
        'EWR': ('Newark', 'NJ'),
        'NYC': ('New York', 'NY'),
        'ORD': ('Chicago', 'IL'),
        'MDW': ('Chicago', 'IL'),
        'DFW': ('Dallas', 'TX'),
        'IAH': ('Houston', 'TX'),
        'HOU': ('Houston', 'TX'),
        'DEN': ('Denver', 'CO'),
        'PHX': ('Phoenix', 'AZ'),
        'SEA': ('Seattle', 'WA'),
        'ATL': ('Atlanta', 'GA'),
        'BOS': ('Boston', 'MA'),
        'MIA': ('Miami', 'FL'),
        'FLL': ('Fort Lauderdale', 'FL'),
        'TPA': ('Tampa', 'FL'),
        'MCO': ('Orlando', 'FL'),
        'MSP': ('Minneapolis', 'MN'),
        'DTW': ('Detroit', 'MI'),
        'PHL': ('Philadelphia', 'PA'),
        'CLT': ('Charlotte', 'NC'),
        'DCA': ('Washington', 'DC'),
        'IAD': ('Washington', 'DC'),
        'BWI': ('Baltimore', 'MD'),
        'SLC': ('Salt Lake City', 'UT'),
        'PDX': ('Portland', 'OR'),
        'LAS': ('Las Vegas', 'NV'),
        'AUS': ('Austin', 'TX'),
        'SAT': ('San Antonio', 'TX'),
        'MSY': ('New Orleans', 'LA'),
        'BNA': ('Nashville', 'TN'),
        'RDU': ('Raleigh', 'NC'),
        'STL': ('St Louis', 'MO'),
        'MKE': ('Milwaukee', 'WI'),
        'CLE': ('Cleveland', 'OH'),
        'CMH': ('Columbus', 'OH'),
        'IND': ('Indianapolis', 'IN'),
        'PIT': ('Pittsburgh', 'PA'),
        'CVG': ('Cincinnati', 'OH'),
        'OKC': ('Oklahoma City', 'OK'),
        'ABQ': ('Albuquerque', 'NM'),
    }

    # City nicknames to actual city mapping
    CITY_NICKNAMES = {
        'big apple': ('New York', 'NY'),
        'the big apple': ('New York', 'NY'),
        'nyc': ('New York', 'NY'),
        'la': ('Los Angeles', 'CA'),
        'windy city': ('Chicago', 'IL'),
        'the windy city': ('Chicago', 'IL'),
        'chi-town': ('Chicago', 'IL'),
        'bay area': ('San Francisco', 'CA'),
        'sf': ('San Francisco', 'CA'),
        'frisco': ('San Francisco', 'CA'),
        'silicon valley': ('San Jose', 'CA'),
        'motor city': ('Detroit', 'MI'),
        'motown': ('Detroit', 'MI'),
        'mile high city': ('Denver', 'CO'),
        'sin city': ('Las Vegas', 'NV'),
        'vegas': ('Las Vegas', 'NV'),
        'philly': ('Philadelphia', 'PA'),
        'hotlanta': ('Atlanta', 'GA'),
        'atl': ('Atlanta', 'GA'),
        'bean town': ('Boston', 'MA'),
        'beantown': ('Boston', 'MA'),
        'big d': ('Dallas', 'TX'),
        'space city': ('Houston', 'TX'),
        'h-town': ('Houston', 'TX'),
        'emerald city': ('Seattle', 'WA'),
        'queen city': ('Charlotte', 'NC'),
        'twin cities': ('Minneapolis', 'MN'),
        'valley of the sun': ('Phoenix', 'AZ'),
        'magic city': ('Miami', 'FL'),
        'music city': ('Nashville', 'TN'),
        'big easy': ('New Orleans', 'LA'),
        'the big easy': ('New Orleans', 'LA'),
        'nola': ('New Orleans', 'LA'),
        'rose city': ('Portland', 'OR'),
        'city of angels': ('Los Angeles', 'CA'),
        'city by the bay': ('San Francisco', 'CA'),
        'charm city': ('Baltimore', 'MD'),
        'steel city': ('Pittsburgh', 'PA'),
        'alamo city': ('San Antonio', 'TX'),
        'circle city': ('Indianapolis', 'IN'),
        'gateway city': ('St Louis', 'MO'),
        'brew city': ('Milwaukee', 'WI'),
        'cream city': ('Milwaukee', 'WI'),
    }

    # Zone database (origin: San Francisco Bay Area)
    ZONE_DATABASE = {
        # Zone 2 - California and nearby
        'san francisco, ca': 2, 'oakland, ca': 2, 'san jose, ca': 2,
        'fremont, ca': 2, 'sacramento, ca': 2, 'fresno, ca': 2,
        'los angeles, ca': 2, 'san diego, ca': 2, 'santa barbara, ca': 2,
        'bakersfield, ca': 2, 'stockton, ca': 2, 'modesto, ca': 2,
        'irvine, ca': 2, 'long beach, ca': 2, 'anaheim, ca': 2,

        # Zone 3 - Pacific Northwest, Southwest
        'phoenix, az': 3, 'tucson, az': 3, 'mesa, az': 3,
        'las vegas, nv': 3, 'reno, nv': 3, 'henderson, nv': 3,
        'portland, or': 3, 'eugene, or': 3, 'salem, or': 3,
        'seattle, wa': 3, 'spokane, wa': 3, 'tacoma, wa': 3,
        'salt lake city, ut': 3, 'provo, ut': 3, 'ogden, ut': 3,
        'denver, co': 3, 'colorado springs, co': 3, 'aurora, co': 3,
        'boulder, co': 3, 'fort collins, co': 3,
        'boise, id': 3, 'albuquerque, nm': 3, 'santa fe, nm': 3,

        # Zone 4 - South Central
        'dallas, tx': 4, 'houston, tx': 4, 'austin, tx': 4,
        'san antonio, tx': 4, 'fort worth, tx': 4, 'el paso, tx': 4,
        'oklahoma city, ok': 4, 'tulsa, ok': 4, 'norman, ok': 4,
        'kansas city, mo': 4, 'st louis, mo': 4, 'springfield, mo': 4,
        'omaha, ne': 4, 'lincoln, ne': 4, 'wichita, ks': 4,
        'little rock, ar': 4, 'des moines, ia': 4, 'sioux falls, sd': 4,

        # Zone 5 - Midwest
        'chicago, il': 5, 'springfield, il': 5, 'peoria, il': 5,
        'detroit, mi': 5, 'grand rapids, mi': 5, 'ann arbor, mi': 5,
        'milwaukee, wi': 5, 'madison, wi': 5, 'green bay, wi': 5,
        'indianapolis, in': 5, 'fort wayne, in': 5, 'evansville, in': 5,
        'columbus, oh': 5, 'cleveland, oh': 5, 'cincinnati, oh': 5,
        'minneapolis, mn': 5, 'st paul, mn': 5, 'duluth, mn': 5,

        # Zone 6 - Southeast
        'atlanta, ga': 6, 'savannah, ga': 6, 'augusta, ga': 6,
        'nashville, tn': 6, 'memphis, tn': 6, 'knoxville, tn': 6,
        'charlotte, nc': 6, 'raleigh, nc': 6, 'durham, nc': 6,
        'miami, fl': 6, 'tampa, fl': 6, 'orlando, fl': 6,
        'jacksonville, fl': 6, 'tallahassee, fl': 6, 'pensacola, fl': 6,
        'fort lauderdale, fl': 6, 'west palm beach, fl': 6,
        'new orleans, la': 6, 'baton rouge, la': 6, 'shreveport, la': 6,
        'birmingham, al': 6, 'montgomery, al': 6, 'mobile, al': 6,
        'jackson, ms': 6, 'charleston, sc': 6, 'columbia, sc': 6,

        # Zone 7 - Mid-Atlantic
        'boston, ma': 7, 'worcester, ma': 7, 'cambridge, ma': 7,
        'philadelphia, pa': 7, 'pittsburgh, pa': 7, 'harrisburg, pa': 7,
        'baltimore, md': 7, 'annapolis, md': 7, 'frederick, md': 7,
        'washington, dc': 7, 'richmond, va': 7, 'norfolk, va': 7,
        'buffalo, ny': 7, 'rochester, ny': 7, 'syracuse, ny': 7,
        'albany, ny': 7, 'hartford, ct': 7, 'new haven, ct': 7,
        'providence, ri': 7, 'portland, me': 7, 'manchester, nh': 7,

        # Zone 8 - New York City Metro
        'new york, ny': 8, 'manhattan, ny': 8, 'brooklyn, ny': 8,
        'queens, ny': 8, 'bronx, ny': 8, 'staten island, ny': 8,
        'newark, nj': 8, 'jersey city, nj': 8, 'paterson, nj': 8,
    }

    # State abbreviations
    STATE_ABBREVIATIONS = {
        'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
        'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
        'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
        'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
        'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
        'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
        'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
        'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
        'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
        'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
        'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
        'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
        'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC'
    }

    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize Zone Calculator.

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

        logger.info(f"ZoneCalculator initialized with {llm_provider}")

    def calculate_zone(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Calculate shipping zone between origin and destination.

        Handles:
        - City names with typos (e.g., "San Fransisco" -> "San Francisco")
        - Airport codes (e.g., "SFO" -> "San Francisco, CA")
        - City nicknames (e.g., "Big Apple" -> "New York, NY")

        Args:
            origin: Origin location (city, airport code, or nickname)
            destination: Destination location (city, airport code, or nickname)

        Returns:
            Dictionary with zone, reasoning, and resolved locations
        """
        logger.info(f"Calculating zone: {origin} -> {destination}")

        trajectory = []

        # Step 1: Resolve origin
        trajectory.append({
            "step": "resolve_origin",
            "input": origin,
            "action": "Resolving origin location"
        })
        origin_city, origin_state, origin_reasoning = self._resolve_location(origin)
        trajectory[-1]["output"] = f"{origin_city}, {origin_state}"
        trajectory[-1]["reasoning"] = origin_reasoning

        # Step 2: Resolve destination
        trajectory.append({
            "step": "resolve_destination",
            "input": destination,
            "action": "Resolving destination location"
        })
        dest_city, dest_state, dest_reasoning = self._resolve_location(destination)
        trajectory[-1]["output"] = f"{dest_city}, {dest_state}"
        trajectory[-1]["reasoning"] = dest_reasoning

        # Step 3: Calculate zone
        trajectory.append({
            "step": "calculate_zone",
            "action": "Looking up zone in database"
        })
        zone, zone_reasoning = self._get_zone(dest_city, dest_state)
        trajectory[-1]["output"] = f"Zone {zone}"
        trajectory[-1]["reasoning"] = zone_reasoning

        return {
            "zone": zone,
            "origin": f"{origin_city}, {origin_state}",
            "destination": f"{dest_city}, {dest_state}",
            "original_origin": origin,
            "original_destination": destination,
            "reasoning": f"Shipping from {origin_city}, {origin_state} to {dest_city}, {dest_state} is Zone {zone}. {zone_reasoning}",
            "trajectory": trajectory,
            "success": zone is not None
        }

    def _resolve_location(self, location: str) -> Tuple[str, str, str]:
        """
        Resolve a location string to city and state.

        Handles airport codes, nicknames, and typos.

        Args:
            location: Raw location string

        Returns:
            Tuple of (city, state, reasoning)
        """
        location_clean = location.strip()
        location_upper = location_clean.upper()
        location_lower = location_clean.lower()

        # Check airport codes first
        if location_upper in self.AIRPORT_CODES:
            city, state = self.AIRPORT_CODES[location_upper]
            return city, state, f"Recognized '{location}' as airport code for {city}, {state}"

        # Check city nicknames
        if location_lower in self.CITY_NICKNAMES:
            city, state = self.CITY_NICKNAMES[location_lower]
            return city, state, f"Recognized '{location}' as nickname for {city}, {state}"

        # Check if it's in "City, State" format
        if ',' in location:
            parts = location.split(',')
            city = parts[0].strip()
            state = parts[1].strip() if len(parts) > 1 else ''

            # Normalize state
            state = self._normalize_state(state)

            # Check for typos in city name using LLM
            corrected_city = self._correct_city_name(city, state)

            if corrected_city.lower() != city.lower():
                return corrected_city, state, f"Corrected city name from '{city}' to '{corrected_city}'"

            return corrected_city, state, f"Parsed as {corrected_city}, {state}"

        # Single word - could be city name, try to infer state
        corrected_city, inferred_state = self._infer_location(location)
        return corrected_city, inferred_state, f"Inferred location as {corrected_city}, {inferred_state}"

    def _normalize_state(self, state: str) -> str:
        """Normalize state name to 2-letter abbreviation."""
        state_upper = state.upper().strip()

        # Already an abbreviation
        if len(state_upper) == 2 and state_upper in self.STATE_ABBREVIATIONS.values():
            return state_upper

        # Full state name
        state_lower = state.lower().strip()
        if state_lower in self.STATE_ABBREVIATIONS:
            return self.STATE_ABBREVIATIONS[state_lower]

        # Try LLM correction
        prompt = f"""Convert this US state to its 2-letter abbreviation.

Input: "{state}"

Return ONLY the 2-letter state code (e.g., CA, NY, TX).
If you cannot determine the state, return "UNKNOWN"."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            normalized = response.content.strip().upper()[:2]
            if normalized in self.STATE_ABBREVIATIONS.values():
                return normalized
        except Exception as e:
            logger.warning(f"State normalization error: {e}")

        return state_upper

    def _correct_city_name(self, city: str, state: str) -> str:
        """Correct city name typos using LLM."""
        # Check if city exists in database as-is
        lookup_key = f"{city.lower()}, {state.lower()}"
        if lookup_key in self.ZONE_DATABASE:
            return city.title()

        # Use LLM to correct
        prompt = f"""Correct this US city name if it has typos.

City: "{city}"
State: {state}

Examples:
- "San Fransisco" -> "San Francisco"
- "Los Angels" -> "Los Angeles"
- "Denvar" -> "Denver"
- "Chicgo" -> "Chicago"
- "Bostun" -> "Boston"

Return ONLY the correctly spelled city name. If the city seems correct, return it as-is."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip().title()
        except Exception as e:
            logger.warning(f"City correction error: {e}")
            return city.title()

    def _infer_location(self, location: str) -> Tuple[str, str]:
        """Infer city and state from a single location name."""
        prompt = f"""Identify this US location and return the city name and state abbreviation.

Location: "{location}"

Consider:
- Major US cities (Denver, Boston, Miami, etc.)
- Common misspellings
- Regional references

Return in this exact format: City, ST
For example: Denver, CO or Boston, MA

If you cannot determine the location, return: Unknown, CA"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()

            if ',' in result:
                parts = result.split(',')
                city = parts[0].strip().title()
                state = parts[1].strip().upper()[:2]
                return city, state
        except Exception as e:
            logger.warning(f"Location inference error: {e}")

        return location.title(), "CA"

    def _get_zone(self, city: str, state: str) -> Tuple[Optional[int], str]:
        """Look up zone for a city/state combination."""
        lookup_key = f"{city.lower()}, {state.lower()}"

        if lookup_key in self.ZONE_DATABASE:
            zone = self.ZONE_DATABASE[lookup_key]
            return zone, f"Found {city}, {state} in zone database"

        # Try partial match
        for key, zone in self.ZONE_DATABASE.items():
            if city.lower() in key:
                return zone, f"Matched {city} approximately in zone database"

        # Fallback: estimate by state
        state_zones = {
            'CA': 2, 'OR': 3, 'WA': 3, 'NV': 3, 'AZ': 3, 'UT': 3, 'CO': 3,
            'ID': 3, 'NM': 3, 'MT': 4, 'WY': 4,
            'TX': 4, 'OK': 4, 'KS': 4, 'NE': 4, 'SD': 4, 'ND': 4,
            'MO': 4, 'AR': 4, 'LA': 5, 'IA': 4,
            'IL': 5, 'MI': 5, 'IN': 5, 'WI': 5, 'MN': 5, 'OH': 5,
            'GA': 6, 'FL': 6, 'SC': 6, 'NC': 6, 'TN': 6, 'AL': 6, 'MS': 6,
            'KY': 6, 'WV': 6, 'VA': 6,
            'PA': 7, 'MA': 7, 'CT': 7, 'RI': 7, 'MD': 7, 'DE': 7,
            'DC': 7, 'ME': 7, 'NH': 7, 'VT': 7,
            'NY': 8, 'NJ': 8
        }

        if state.upper() in state_zones:
            zone = state_zones[state.upper()]
            return zone, f"Estimated zone based on state {state}"

        return 5, "Default zone estimate"

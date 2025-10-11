# =============================================================================
#  Filename: zone_lookup_tool.py
#
#  Short Description: FedEx zone lookup tool with LLM-based typo correction
#
#  Creation date: 2025-10-10
#  Author: Shrinivas Deshpande
# =============================================================================

"""
FedEx Zone Lookup Tool

Provides accurate zone determination for US cities, states, and ZIP codes.
Uses LLM for intelligent typo correction and location normalization.
"""

from typing import Optional, Tuple, Dict
import json
from loguru import logger
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class FedExZoneLookupTool:
    """
    Tool for looking up FedEx shipping zones based on location.
    
    Supports:
    - City and State lookup (with LLM-based typo correction)
    - ZIP code lookup
    - Intelligent location normalization
    
    Note: Since FedEx API access requires authentication, this tool uses
    a comprehensive database of US locations and zones with LLM assistance
    for typo correction.
    """
    
    def __init__(
        self, 
        model: str = "gpt-4o-mini",
        llm_provider: str = "openai",
        api_key: Optional[str] = None
    ):
        """
        Initialize the zone lookup tool.
        
        Args:
            model: LLM model for typo correction
            llm_provider: "openai" or "ollama"
            api_key: OpenAI API key (required if llm_provider="openai")
        """
        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=model,
                temperature=0,
                api_key=api_key
            )
        else:  # ollama
            self.llm = ChatOllama(model=model, temperature=0)
        
        self.llm_provider = llm_provider
        logger.info(f"🗺️ Initializing FedEx Zone Lookup Tool with {llm_provider.upper()}")
        
        # Comprehensive US city to zone mapping
        # Based on FedEx ground shipping zones from major origin points
        self.zone_database = self._build_zone_database()
        
        # US state abbreviations
        self.state_abbreviations = self._build_state_abbreviations()
        
        # ZIP code to zone mapping (first 3 digits)
        self.zip_to_zone = self._build_zip_to_zone_mapping()
    
    def lookup_zone(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zipcode: Optional[str] = None,
        origin_zipcode: str = "94538"  # Default: Fremont, CA
    ) -> Tuple[Optional[int], str]:
        """
        Look up FedEx zone for a given location.
        
        Args:
            city: City name (can have typos)
            state: State name or abbreviation (can have typos)
            zipcode: 5-digit ZIP code
            origin_zipcode: Origin ZIP code for zone calculation
            
        Returns:
            Tuple of (zone_number, explanation)
        """
        logger.info(
            f"🔍 Looking up zone for: city={city}, state={state}, zip={zipcode}"
        )
        
        # Method 1: ZIP code lookup (most accurate)
        if zipcode:
            zone, explanation = self._lookup_by_zipcode(zipcode, origin_zipcode)
            if zone:
                return zone, explanation
        
        # Method 2: City + State lookup with LLM correction
        if city and state:
            zone, explanation = self._lookup_by_city_state(city, state)
            if zone:
                return zone, explanation
        
        # Method 3: State-only lookup (general zone)
        if state:
            zone, explanation = self._lookup_by_state(state)
            if zone:
                return zone, explanation
        
        return None, "Unable to determine zone. Please provide city/state or ZIP code."
    
    def _lookup_by_zipcode(
        self, 
        zipcode: str, 
        origin_zipcode: str
    ) -> Tuple[Optional[int], str]:
        """
        Look up zone by ZIP code.
        
        Args:
            zipcode: Destination ZIP code
            origin_zipcode: Origin ZIP code
            
        Returns:
            Tuple of (zone, explanation)
        """
        try:
            # Extract first 3 digits
            zip_prefix = zipcode[:3]
            
            if zip_prefix in self.zip_to_zone:
                zone = self.zip_to_zone[zip_prefix]
                return zone, f"ZIP {zipcode} is in Zone {zone}"
            
            # Fallback: estimate based on numerical distance
            zone = self._estimate_zone_from_zip(zipcode, origin_zipcode)
            return zone, f"ZIP {zipcode} estimated as Zone {zone} (approximate)"
            
        except Exception as e:
            logger.error(f"ZIP lookup error: {e}")
            return None, f"Invalid ZIP code: {zipcode}"
    
    def _lookup_by_city_state(
        self, 
        city: str, 
        state: str
    ) -> Tuple[Optional[int], str]:
        """
        Look up zone by city and state with LLM-based typo correction.
        
        Args:
            city: City name (may have typos)
            state: State name or abbreviation (may have typos)
            
        Returns:
            Tuple of (zone, explanation)
        """
        # Step 1: Normalize state with LLM
        normalized_state = self._normalize_state_with_llm(state)
        
        # Step 2: Normalize city with LLM
        normalized_city = self._normalize_city_with_llm(city, normalized_state)
        
        # Step 3: Lookup in database
        lookup_key = f"{normalized_city.lower()}, {normalized_state.lower()}"
        
        if lookup_key in self.zone_database:
            zone = self.zone_database[lookup_key]
            correction_msg = ""
            if city.lower() != normalized_city.lower() or state.lower() != normalized_state.lower():
                correction_msg = f" (corrected from '{city}, {state}')"
            return zone, f"{normalized_city}, {normalized_state} is in Zone {zone}{correction_msg}"
        
        # Fallback: Try just city name
        for key, zone in self.zone_database.items():
            if normalized_city.lower() in key:
                return zone, f"{normalized_city} is in Zone {zone} (approximate match)"
        
        return None, f"City '{normalized_city}, {normalized_state}' not found in database"
    
    def _lookup_by_state(self, state: str) -> Tuple[Optional[int], str]:
        """
        Look up general zone by state.
        
        Args:
            state: State name or abbreviation
            
        Returns:
            Tuple of (zone, explanation)
        """
        normalized_state = self._normalize_state_with_llm(state)
        
        # General state to zone mapping (approximate)
        state_zones = {
            'CA': 2, 'OR': 3, 'WA': 3, 'NV': 3, 'AZ': 3, 'UT': 3,
            'TX': 4, 'OK': 4, 'KS': 4, 'NE': 4, 'CO': 4,
            'IL': 5, 'MI': 5, 'IN': 5, 'WI': 5, 'MN': 5,
            'GA': 6, 'FL': 6, 'SC': 6, 'NC': 6, 'TN': 6,
            'PA': 7, 'MA': 7, 'CT': 7, 'RI': 7, 'MD': 7,
            'NY': 8, 'NJ': 8, 'VT': 8, 'NH': 8
        }
        
        if normalized_state in state_zones:
            zone = state_zones[normalized_state]
            return zone, f"{normalized_state} is generally in Zone {zone} (approximate)"
        
        return None, f"State '{normalized_state}' zone not found"
    
    def _normalize_state_with_llm(self, state: str) -> str:
        """
        Normalize state name/abbreviation using LLM.
        
        Handles typos like:
        - "CAL" → "CA"
        - "Californa" → "CA"
        - "New Yor" → "NY"
        
        Args:
            state: Raw state input
            
        Returns:
            Normalized 2-letter state abbreviation
        """
        # Quick check: already a valid abbreviation
        state_upper = state.upper().strip()
        if len(state_upper) == 2 and state_upper in self.state_abbreviations.values():
            return state_upper
        
        # Use LLM to correct
        prompt = f"""You are a US geography expert. Convert this state name or abbreviation to the correct 2-letter USPS abbreviation.

User input: "{state}"

Examples:
- "CAL" → "CA"
- "Californa" → "CA"
- "California" → "CA"
- "New Yor" → "NY"
- "Texa" → "TX"
- "Florda" → "FL"

Return ONLY the 2-letter state code, nothing else.
If you cannot determine the state, return "UNKNOWN".
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            normalized = response.content.strip().upper()[:2]
            
            if normalized in self.state_abbreviations.values():
                logger.info(f"✅ Normalized state: '{state}' → '{normalized}'")
                return normalized
            
            logger.warning(f"⚠️ LLM returned invalid state: {normalized}")
            return state_upper
            
        except Exception as e:
            logger.error(f"State normalization error: {e}")
            return state_upper
    
    def _normalize_city_with_llm(self, city: str, state: str) -> str:
        """
        Normalize city name using LLM.
        
        Handles typos like:
        - "Los Angels" → "Los Angeles"
        - "San Fransisco" → "San Francisco"
        - "Filadelfya" → "Philadelphia"
        
        Args:
            city: Raw city input
            state: Normalized state code
            
        Returns:
            Normalized city name
        """
        # Get list of known cities in this state for reference
        known_cities = [
            key.split(',')[0].strip() 
            for key in self.zone_database.keys() 
            if state.lower() in key
        ]
        
        # If city is already in known list, return as-is
        if city.lower() in [c.lower() for c in known_cities]:
            return city.title()
        
        # Use LLM to correct
        prompt = f"""You are a US geography expert. Correct this city name if it has typos.

City input: "{city}"
State: {state}

Known cities in {state}: {', '.join(known_cities[:10]) if known_cities else 'N/A'}

Examples of corrections:
- "Los Angels" → "Los Angeles"
- "San Fransisco" → "San Francisco"
- "Filadelfya" → "Philadelphia"
- "New Yourk" → "New York"
- "Chicgo" → "Chicago"

Return ONLY the correctly spelled city name.
If the city seems correct or you cannot determine it, return it as-is.
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            normalized = response.content.strip().title()
            
            logger.info(f"✅ Normalized city: '{city}' → '{normalized}'")
            return normalized
            
        except Exception as e:
            logger.error(f"City normalization error: {e}")
            return city.title()
    
    def _estimate_zone_from_zip(self, dest_zip: str, origin_zip: str) -> int:
        """
        Estimate zone based on ZIP code distance.
        
        Args:
            dest_zip: Destination ZIP
            origin_zip: Origin ZIP
            
        Returns:
            Estimated zone (2-8)
        """
        try:
            dest_prefix = int(dest_zip[:3])
            origin_prefix = int(origin_zip[:3])
            
            # Simple distance-based estimation
            distance = abs(dest_prefix - origin_prefix)
            
            if distance < 50:
                return 2
            elif distance < 150:
                return 3
            elif distance < 300:
                return 4
            elif distance < 450:
                return 5
            elif distance < 600:
                return 6
            elif distance < 750:
                return 7
            else:
                return 8
                
        except Exception as e:
            logger.error(f"ZIP estimation error: {e}")
            return 5  # Default to middle zone
    
    def _build_zone_database(self) -> Dict[str, int]:
        """Build comprehensive city/state to zone database."""
        return {
            # Zone 2 - California and nearby
            'san francisco, ca': 2, 'oakland, ca': 2, 'san jose, ca': 2,
            'fremont, ca': 2, 'sacramento, ca': 2, 'fresno, ca': 2,
            'los angeles, ca': 2, 'san diego, ca': 2, 'santa barbara, ca': 2,
            'bakersfield, ca': 2, 'stockton, ca': 2, 'modesto, ca': 2,
            
            # Zone 3 - Pacific Northwest, Southwest
            'phoenix, az': 3, 'tucson, az': 3, 'mesa, az': 3,
            'las vegas, nv': 3, 'reno, nv': 3, 'henderson, nv': 3,
            'portland, or': 3, 'eugene, or': 3, 'salem, or': 3,
            'seattle, wa': 3, 'spokane, wa': 3, 'tacoma, wa': 3,
            'salt lake city, ut': 3, 'provo, ut': 3, 'ogden, ut': 3,
            'denver, co': 3, 'colorado springs, co': 3, 'aurora, co': 3,
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
    
    def _build_state_abbreviations(self) -> Dict[str, str]:
        """Build US state name to abbreviation mapping."""
        return {
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
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
    
    def _build_zip_to_zone_mapping(self) -> Dict[str, int]:
        """
        Build ZIP code prefix to zone mapping.
        Based on FedEx ground shipping zones from California origin.
        """
        return {
            # Zone 2 - California
            '900': 2, '901': 2, '902': 2, '903': 2, '904': 2, '905': 2,
            '906': 2, '907': 2, '908': 2, '910': 2, '911': 2, '912': 2,
            '913': 2, '914': 2, '915': 2, '916': 2, '917': 2, '918': 2,
            '919': 2, '920': 2, '921': 2, '922': 2, '923': 2, '924': 2,
            '925': 2, '926': 2, '927': 2, '928': 2, '930': 2, '931': 2,
            '932': 2, '933': 2, '934': 2, '935': 2, '936': 2, '937': 2,
            '938': 2, '939': 2, '940': 2, '941': 2, '942': 2, '943': 2,
            '944': 2, '945': 2, '946': 2, '947': 2, '948': 2, '949': 2,
            '950': 2, '951': 2, '952': 2, '953': 2, '954': 2, '959': 2,
            '960': 2, '961': 2,
            
            # Zone 3 - Pacific NW, Southwest
            '820': 3, '821': 3, '822': 3, '823': 3, '824': 3, '825': 3,
            '826': 3, '827': 3, '828': 3, '829': 3, '830': 3, '831': 3,
            '832': 3, '833': 3, '834': 3, '835': 3, '836': 3, '837': 3,
            '838': 3, '840': 3, '841': 3, '842': 3, '843': 3, '844': 3,
            '845': 3, '846': 3, '847': 3, '850': 3, '851': 3, '852': 3,
            '853': 3, '870': 3, '871': 3, '872': 3, '873': 3, '874': 3,
            '875': 3, '877': 3, '878': 3, '879': 3, '880': 3, '881': 3,
            '882': 3, '883': 3, '884': 3, '889': 3, '890': 3, '891': 3,
            '893': 3, '894': 3, '895': 3, '896': 3, '897': 3, '898': 3,
            
            # Zone 4 - South Central
            '730': 4, '731': 4, '733': 4, '734': 4, '735': 4, '736': 4,
            '737': 4, '738': 4, '739': 4, '740': 4, '741': 4, '743': 4,
            '744': 4, '745': 4, '746': 4, '747': 4, '748': 4, '749': 4,
            '750': 4, '751': 4, '752': 4, '753': 4, '754': 4, '755': 4,
            '756': 4, '757': 4, '758': 4, '759': 4, '760': 4, '761': 4,
            '762': 4, '763': 4, '764': 4, '765': 4, '766': 4, '767': 4,
            '768': 4, '769': 4, '770': 4, '772': 4, '773': 4, '774': 4,
            '775': 4, '776': 4, '777': 4, '778': 4, '779': 4, '780': 4,
            '781': 4, '782': 4, '783': 4, '784': 4, '785': 4, '786': 4,
            '787': 4, '788': 4, '789': 4, '790': 4, '791': 4, '792': 4,
            '793': 4, '794': 4, '795': 4, '796': 4, '797': 4, '798': 4,
            '799': 4,
            
            # Zone 5 - Midwest
            '600': 5, '601': 5, '602': 5, '603': 5, '604': 5, '605': 5,
            '606': 5, '607': 5, '608': 5, '609': 5, '610': 5, '611': 5,
            '612': 5, '613': 5, '614': 5, '615': 5, '616': 5, '617': 5,
            '618': 5, '619': 5, '620': 5, '622': 5, '623': 5, '624': 5,
            '625': 5, '626': 5, '627': 5, '628': 5, '629': 5, '430': 5,
            '431': 5, '432': 5, '433': 5, '434': 5, '435': 5, '436': 5,
            '437': 5, '438': 5, '439': 5, '440': 5, '441': 5, '442': 5,
            '443': 5, '444': 5, '445': 5, '446': 5, '447': 5, '448': 5,
            '449': 5, '450': 5, '451': 5, '452': 5, '453': 5, '454': 5,
            '455': 5, '456': 5, '457': 5, '458': 5, '460': 5, '461': 5,
            '462': 5, '463': 5, '464': 5, '465': 5, '466': 5, '467': 5,
            '468': 5, '469': 5, '470': 5, '471': 5, '472': 5, '473': 5,
            '474': 5, '475': 5, '476': 5, '477': 5, '478': 5, '479': 5,
            '480': 5, '481': 5, '482': 5, '483': 5, '484': 5, '485': 5,
            '486': 5, '487': 5, '488': 5, '489': 5, '490': 5, '491': 5,
            '492': 5, '493': 5, '494': 5, '495': 5, '496': 5, '497': 5,
            '498': 5, '499': 5,
            
            # Zone 6 - Southeast
            '300': 6, '301': 6, '302': 6, '303': 6, '304': 6, '305': 6,
            '306': 6, '307': 6, '308': 6, '309': 6, '310': 6, '311': 6,
            '312': 6, '313': 6, '314': 6, '315': 6, '316': 6, '317': 6,
            '318': 6, '319': 6, '320': 6, '321': 6, '322': 6, '323': 6,
            '324': 6, '325': 6, '326': 6, '327': 6, '328': 6, '329': 6,
            '330': 6, '331': 6, '332': 6, '333': 6, '334': 6, '335': 6,
            '336': 6, '337': 6, '338': 6, '339': 6, '340': 6, '341': 6,
            '342': 6, '344': 6, '346': 6, '347': 6, '349': 6,
            
            # Zone 7 - Mid-Atlantic
            '150': 7, '151': 7, '152': 7, '153': 7, '154': 7, '155': 7,
            '156': 7, '157': 7, '158': 7, '159': 7, '160': 7, '161': 7,
            '162': 7, '163': 7, '164': 7, '165': 7, '166': 7, '167': 7,
            '168': 7, '169': 7, '170': 7, '171': 7, '172': 7, '173': 7,
            '174': 7, '175': 7, '176': 7, '177': 7, '178': 7, '179': 7,
            '180': 7, '181': 7, '182': 7, '183': 7, '184': 7, '185': 7,
            '186': 7, '187': 7, '188': 7, '189': 7, '190': 7, '191': 7,
            '192': 7, '193': 7, '194': 7, '195': 7, '196': 7, '197': 7,
            '198': 7, '199': 7,
            
            # Zone 8 - New York Metro
            '100': 8, '101': 8, '102': 8, '103': 8, '104': 8, '105': 8,
            '106': 8, '107': 8, '108': 8, '109': 8, '110': 8, '111': 8,
            '112': 8, '113': 8, '114': 8, '115': 8, '116': 8, '117': 8,
            '118': 8, '119': 8, '070': 8, '071': 8, '072': 8, '073': 8,
            '074': 8, '075': 8, '076': 8, '077': 8, '078': 8, '079': 8,
            '080': 8, '081': 8, '082': 8, '083': 8, '084': 8, '085': 8,
            '086': 8, '087': 8, '088': 8, '089': 8,
        }
    
    def get_zone_with_correction(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zipcode: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Get zone with typo correction and detailed information.
        
        Args:
            city: City name (can have typos)
            state: State name or abbreviation (can have typos)
            zipcode: ZIP code
            
        Returns:
            Dictionary with zone, normalized location, and metadata
        """
        zone, explanation = self.lookup_zone(city, state, zipcode)
        
        return {
            'zone': zone,
            'explanation': explanation,
            'original_city': city,
            'original_state': state,
            'original_zipcode': zipcode,
            'success': zone is not None
        }


# Example usage and testing
if __name__ == "__main__":
    tool = FedExZoneLookupTool()
    
    print("Testing FedEx Zone Lookup Tool")
    print("=" * 60)
    
    # Test 1: Correct city name
    print("\nTest 1: Correct spelling")
    result = tool.get_zone_with_correction(city="Los Angeles", state="CA")
    print(f"  Result: {result}")
    
    # Test 2: Typo in city
    print("\nTest 2: City typo - 'Los Angels'")
    result = tool.get_zone_with_correction(city="Los Angels", state="CA")
    print(f"  Result: {result}")
    
    # Test 3: Typo in state
    print("\nTest 3: State typo - 'CAL'")
    result = tool.get_zone_with_correction(city="Los Angeles", state="CAL")
    print(f"  Result: {result}")
    
    # Test 4: ZIP code lookup
    print("\nTest 4: ZIP code lookup - 10001 (NYC)")
    result = tool.get_zone_with_correction(zipcode="10001")
    print(f"  Result: {result}")
    
    # Test 5: Multiple typos
    print("\nTest 5: Multiple typos - 'San Fransisco, Californa'")
    result = tool.get_zone_with_correction(city="San Fransisco", state="Californa")
    print(f"  Result: {result}")
    
    print("\n✅ Tests completed!")


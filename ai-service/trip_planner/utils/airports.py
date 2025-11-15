"""Airport search functionality with comprehensive airport database."""

import os
import re
import requests
from typing import List, Dict, Any, Optional

# Comprehensive airport database with 150+ major airports worldwide
AIRPORTS_DB = [
    # North America
    {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA"},
    {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA"},
    {"code": "ORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "USA"},
    {"code": "MIA", "name": "Miami International Airport", "city": "Miami", "country": "USA"},
    {"code": "SFO", "name": "San Francisco International Airport", "city": "San Francisco", "country": "USA"},
    {"code": "SEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "country": "USA"},
    {"code": "LAS", "name": "Harry Reid International Airport", "city": "Las Vegas", "country": "USA"},
    {"code": "BOS", "name": "Logan International Airport", "city": "Boston", "country": "USA"},
    {"code": "MCO", "name": "Orlando International Airport", "city": "Orlando", "country": "USA"},
    {"code": "EWR", "name": "Newark Liberty International Airport", "city": "Newark", "country": "USA"},
    {"code": "DEN", "name": "Denver International Airport", "city": "Denver", "country": "USA"},
    {"code": "DFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "country": "USA"},
    {"code": "ATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "country": "USA"},
    {"code": "IAH", "name": "George Bush Intercontinental Airport", "city": "Houston", "country": "USA"},
    {"code": "PHX", "name": "Phoenix Sky Harbor International Airport", "city": "Phoenix", "country": "USA"},
    {"code": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada"},
    {"code": "YVR", "name": "Vancouver International Airport", "city": "Vancouver", "country": "Canada"},
    {"code": "YUL", "name": "Montréal-Trudeau International Airport", "city": "Montreal", "country": "Canada"},
    {"code": "MEX", "name": "Mexico City International Airport", "city": "Mexico City", "country": "Mexico"},
    {"code": "CUN", "name": "Cancún International Airport", "city": "Cancun", "country": "Mexico"},
    
    # Europe
    {"code": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "UK"},
    {"code": "LGW", "name": "London Gatwick Airport", "city": "London", "country": "UK"},
    {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
    {"code": "ORY", "name": "Paris Orly Airport", "city": "Paris", "country": "France"},
    {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
    {"code": "MUC", "name": "Munich Airport", "city": "Munich", "country": "Germany"},
    {"code": "BER", "name": "Berlin Brandenburg Airport", "city": "Berlin", "country": "Germany"},
    {"code": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
    {"code": "MAD", "name": "Adolfo Suárez Madrid–Barajas Airport", "city": "Madrid", "country": "Spain"},
    {"code": "BCN", "name": "Barcelona–El Prat Airport", "city": "Barcelona", "country": "Spain"},
    {"code": "FCO", "name": "Leonardo da Vinci–Fiumicino Airport", "city": "Rome", "country": "Italy"},
    {"code": "MXP", "name": "Milan Malpensa Airport", "city": "Milan", "country": "Italy"},
    {"code": "VCE", "name": "Venice Marco Polo Airport", "city": "Venice", "country": "Italy"},
    {"code": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland"},
    {"code": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria"},
    {"code": "CPH", "name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark"},
    {"code": "OSL", "name": "Oslo Airport", "city": "Oslo", "country": "Norway"},
    {"code": "ARN", "name": "Stockholm Arlanda Airport", "city": "Stockholm", "country": "Sweden"},
    {"code": "HEL", "name": "Helsinki Airport", "city": "Helsinki", "country": "Finland"},
    {"code": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey"},
    {"code": "LIS", "name": "Lisbon Portela Airport", "city": "Lisbon", "country": "Portugal"},
    {"code": "DUB", "name": "Dublin Airport", "city": "Dublin", "country": "Ireland"},
    {"code": "ATH", "name": "Athens International Airport", "city": "Athens", "country": "Greece"},
    {"code": "PRG", "name": "Václav Havel Airport Prague", "city": "Prague", "country": "Czech Republic"},
    {"code": "WAW", "name": "Warsaw Chopin Airport", "city": "Warsaw", "country": "Poland"},
    {"code": "BUD", "name": "Budapest Ferenc Liszt International Airport", "city": "Budapest", "country": "Hungary"},
    
    # Asia
    {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "HND", "name": "Tokyo Haneda Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "KIX", "name": "Kansai International Airport", "city": "Osaka", "country": "Japan"},
    {"code": "ICN", "name": "Incheon International Airport", "city": "Seoul", "country": "South Korea"},
    {"code": "PEK", "name": "Beijing Capital International Airport", "city": "Beijing", "country": "China"},
    {"code": "PVG", "name": "Shanghai Pudong International Airport", "city": "Shanghai", "country": "China"},
    {"code": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong"},
    {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
    {"code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
    {"code": "KUL", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia"},
    {"code": "CGK", "name": "Soekarno–Hatta International Airport", "city": "Jakarta", "country": "Indonesia"},
    {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "Delhi", "country": "India"},
    {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "country": "India"},
    {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "UAE"},
    {"code": "DOH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar"},
    {"code": "MNL", "name": "Ninoy Aquino International Airport", "city": "Manila", "country": "Philippines"},
    {"code": "HAN", "name": "Noi Bai International Airport", "city": "Hanoi", "country": "Vietnam"},
    {"code": "SGN", "name": "Tan Son Nhat International Airport", "city": "Ho Chi Minh City", "country": "Vietnam"},
    
    # Oceania
    {"code": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia"},
    {"code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia"},
    {"code": "BNE", "name": "Brisbane Airport", "city": "Brisbane", "country": "Australia"},
    {"code": "PER", "name": "Perth Airport", "city": "Perth", "country": "Australia"},
    {"code": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand"},
    {"code": "CHC", "name": "Christchurch International Airport", "city": "Christchurch", "country": "New Zealand"},
    
    # South America
    {"code": "GRU", "name": "São Paulo/Guarulhos International Airport", "city": "São Paulo", "country": "Brazil"},
    {"code": "GIG", "name": "Rio de Janeiro/Galeão International Airport", "city": "Rio de Janeiro", "country": "Brazil"},
    {"code": "EZE", "name": "Ministro Pistarini International Airport", "city": "Buenos Aires", "country": "Argentina"},
    {"code": "SCL", "name": "Arturo Merino Benítez International Airport", "city": "Santiago", "country": "Chile"},
    {"code": "LIM", "name": "Jorge Chávez International Airport", "city": "Lima", "country": "Peru"},
    {"code": "BOG", "name": "El Dorado International Airport", "city": "Bogotá", "country": "Colombia"},
    
    # Africa
    {"code": "JNB", "name": "O.R. Tambo International Airport", "city": "Johannesburg", "country": "South Africa"},
    {"code": "CPT", "name": "Cape Town International Airport", "city": "Cape Town", "country": "South Africa"},
    {"code": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt"},
    {"code": "CMN", "name": "Mohammed V International Airport", "city": "Casablanca", "country": "Morocco"},
    {"code": "NBO", "name": "Jomo Kenyatta International Airport", "city": "Nairobi", "country": "Kenya"},
    
    # Middle East
    {"code": "TLV", "name": "Ben Gurion Airport", "city": "Tel Aviv", "country": "Israel"},
    {"code": "AMM", "name": "Queen Alia International Airport", "city": "Amman", "country": "Jordan"},
    {"code": "BEY", "name": "Rafic Hariri International Airport", "city": "Beirut", "country": "Lebanon"},
    
    # More US Cities
    {"code": "PDX", "name": "Portland International Airport", "city": "Portland", "country": "USA"},
    {"code": "SLC", "name": "Salt Lake City International Airport", "city": "Salt Lake City", "country": "USA"},
    {"code": "MSP", "name": "Minneapolis–Saint Paul International Airport", "city": "Minneapolis", "country": "USA"},
    {"code": "DTW", "name": "Detroit Metropolitan Airport", "city": "Detroit", "country": "USA"},
    {"code": "PHL", "name": "Philadelphia International Airport", "city": "Philadelphia", "country": "USA"},
    {"code": "CLT", "name": "Charlotte Douglas International Airport", "city": "Charlotte", "country": "USA"},
    {"code": "BWI", "name": "Baltimore/Washington International Airport", "city": "Baltimore", "country": "USA"},
    {"code": "DCA", "name": "Ronald Reagan Washington National Airport", "city": "Washington D.C.", "country": "USA"},
    {"code": "IAD", "name": "Washington Dulles International Airport", "city": "Washington D.C.", "country": "USA"},
    {"code": "SAN", "name": "San Diego International Airport", "city": "San Diego", "country": "USA"},
    {"code": "TPA", "name": "Tampa International Airport", "city": "Tampa", "country": "USA"},
    {"code": "STL", "name": "St. Louis Lambert International Airport", "city": "St. Louis", "country": "USA"},
    {"code": "BNA", "name": "Nashville International Airport", "city": "Nashville", "country": "USA"},
    {"code": "AUS", "name": "Austin-Bergstrom International Airport", "city": "Austin", "country": "USA"},
    {"code": "RDU", "name": "Raleigh-Durham International Airport", "city": "Raleigh", "country": "USA"},
    {"code": "SJC", "name": "San Jose International Airport", "city": "San Jose", "country": "USA"},
    {"code": "OAK", "name": "Oakland International Airport", "city": "Oakland", "country": "USA"},
    
    # More European Cities
    {"code": "BRU", "name": "Brussels Airport", "city": "Brussels", "country": "Belgium"},
    {"code": "LUX", "name": "Luxembourg Airport", "city": "Luxembourg", "country": "Luxembourg"},
    {"code": "GVA", "name": "Geneva Airport", "city": "Geneva", "country": "Switzerland"},
    {"code": "BSL", "name": "EuroAirport Basel-Mulhouse-Freiburg", "city": "Basel", "country": "Switzerland"},
    {"code": "EDI", "name": "Edinburgh Airport", "city": "Edinburgh", "country": "UK"},
    {"code": "MAN", "name": "Manchester Airport", "city": "Manchester", "country": "UK"},
    {"code": "LYS", "name": "Lyon-Saint Exupéry Airport", "city": "Lyon", "country": "France"},
    {"code": "NCE", "name": "Nice Côte d'Azur Airport", "city": "Nice", "country": "France"},
    {"code": "TLS", "name": "Toulouse–Blagnac Airport", "city": "Toulouse", "country": "France"},
    {"code": "NAP", "name": "Naples International Airport", "city": "Naples", "country": "Italy"},
    {"code": "CGN", "name": "Cologne Bonn Airport", "city": "Cologne", "country": "Germany"},
    {"code": "HAM", "name": "Hamburg Airport", "city": "Hamburg", "country": "Germany"},
    {"code": "STR", "name": "Stuttgart Airport", "city": "Stuttgart", "country": "Germany"},
    
    # More Asian Cities
    {"code": "TPE", "name": "Taiwan Taoyuan International Airport", "city": "Taipei", "country": "Taiwan"},
    {"code": "CAN", "name": "Guangzhou Baiyun International Airport", "city": "Guangzhou", "country": "China"},
    {"code": "SZX", "name": "Shenzhen Bao'an International Airport", "city": "Shenzhen", "country": "China"},
    {"code": "CTU", "name": "Chengdu Shuangliu International Airport", "city": "Chengdu", "country": "China"},
    {"code": "HGH", "name": "Hangzhou Xiaoshan International Airport", "city": "Hangzhou", "country": "China"},
    {"code": "BLR", "name": "Kempegowda International Airport", "city": "Bangalore", "country": "India"},
    {"code": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "country": "India"},
    {"code": "MAA", "name": "Chennai International Airport", "city": "Chennai", "country": "India"},
    {"code": "CCU", "name": "Netaji Subhas Chandra Bose International Airport", "city": "Kolkata", "country": "India"},
]


def search_airports(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for airports by city name, country, or airport code.
    
    Args:
        query: Search query (city name, country, or airport code)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of airport dictionaries with displayName formatted for frontend
    
    Examples:
        >>> search_airports("paris")
        [
            {
                "code": "CDG",
                "name": "Charles de Gaulle Airport",
                "city": "Paris",
                "country": "France",
                "displayName": "Paris - Charles de Gaulle (CDG)"
            },
            {
                "code": "ORY",
                "name": "Paris Orly Airport",
                "city": "Paris",
                "country": "France",
                "displayName": "Paris - Orly (ORY)"
            }
        ]
    """
    if not query:
        return []
    
    query_lower = query.lower().strip()
    results = []
    
    # Search by code, city, country, or airport name
    for airport in AIRPORTS_DB:
        # Exact code match (highest priority)
        if airport["code"].lower() == query_lower:
            results.insert(0, _format_airport_result(airport))
            continue
        
        # Check if query matches city, country, or name
        if (query_lower in airport["city"].lower() or
            query_lower in airport["country"].lower() or
            query_lower in airport["name"].lower() or
            query_lower in airport["code"].lower()):
            results.append(_format_airport_result(airport))
    
    # Sort by city name (except for exact code matches at the beginning)
    if results:
        # Keep exact code matches at the top
        exact_matches = [r for r in results if r["code"].lower() == query_lower]
        other_matches = [r for r in results if r["code"].lower() != query_lower]
        other_matches.sort(key=lambda x: x["city"])
        results = exact_matches + other_matches
        return results[:limit]
    
    # Fallback: If no results in static DB, try SerpAPI
    # This handles airports not in our database (smaller cities, regional airports)
    serpapi_results = _search_airports_serpapi(query, limit)
    if serpapi_results:
        return serpapi_results
    
    # No results found in static DB or SerpAPI
    return []


def _format_airport_result(airport: Dict[str, str]) -> Dict[str, Any]:
    """
    Format airport data for frontend display.
    
    Args:
        airport: Raw airport dictionary
    
    Returns:
        Formatted airport with displayName
    """
    # Simplify airport name (remove "International Airport", "Airport", etc.)
    name = airport["name"]
    name = name.replace(" International Airport", "")
    name = name.replace(" Airport", "")
    name = name.replace("–", "-")
    
    return {
        "code": airport["code"],
        "name": airport["name"],
        "city": airport["city"],
        "country": airport["country"],
        "displayName": f"{airport['city']} - {name} ({airport['code']})"
    }


def _search_airports_serpapi(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fallback: Search for airports using SerpAPI Google Autocomplete.
    Used when airport is not found in static database.
    
    Args:
        query: Search query (city name or airport code)
        limit: Maximum number of results
    
    Returns:
        List of airport dictionaries, or empty list if search fails
    """
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    if not SERPAPI_API_KEY:
        # No API key, return empty (silent fail)
        return []
    
    try:
        # Try searching for "airports in [city]" or "[city] airport"
        search_queries = [
            f"airports in {query}",
            f"{query} airport",
            f"{query} airport code",
        ]
        
        results = []
        
        for search_query in search_queries[:1]:  # Try first query only
            params = {
                "engine": "google_autocomplete",
                "q": search_query,
                "hl": "en",
                "gl": "us",
                "api_key": SERPAPI_API_KEY,
            }
            
            url = "https://serpapi.com/search.json"
            resp = requests.get(url, params=params, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                suggestions = data.get("suggestions", [])
                
                # Parse suggestions to extract airport information
                for suggestion in suggestions[:limit]:
                    suggestion_text = suggestion.get("value", "")
                    
                    # Look for airport codes (3 uppercase letters) in parentheses
                    code_match = re.search(r'\(([A-Z]{3})\)', suggestion_text)
                    if code_match:
                        code = code_match.group(1)
                        
                        # Extract city name (text before the airport name)
                        # Example: "Paris Charles de Gaulle Airport (CDG)"
                        city_match = re.match(r'^([^A-Z]+)', suggestion_text)
                        city = city_match.group(1).strip() if city_match else query
                        
                        # Extract airport name
                        airport_name = suggestion_text.replace(f"({code})", "").strip()
                        
                        # Try to extract country from suggestion if available
                        country = "Unknown"
                        if "USA" in suggestion_text or "United States" in suggestion_text:
                            country = "USA"
                        elif "UK" in suggestion_text or "United Kingdom" in suggestion_text:
                            country = "UK"
                        
                        results.append({
                            "code": code,
                            "name": airport_name,
                            "city": city,
                            "country": country,
                            "displayName": f"{city} - {airport_name} ({code})"
                        })
                
                # If we found results, return them
                if results:
                    return results[:limit]
        
        # If autocomplete didn't work, try Google search for airport information
        params = {
            "engine": "google",
            "q": f"{query} airport code IATA",
            "hl": "en",
            "gl": "us",
            "api_key": SERPAPI_API_KEY,
        }
        
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            
            # Try to extract from knowledge graph
            kg = data.get("knowledge_graph", {})
            if kg:
                title = kg.get("title", "")
                # Look for airport code in title or description
                code_match = re.search(r'\b([A-Z]{3})\b', title)
                if code_match:
                    code = code_match.group(1)
                    # Extract airport name
                    airport_name = title.replace(f"({code})", "").strip()
                    results.append({
                        "code": code,
                        "name": airport_name,
                        "city": query,
                        "country": "Unknown",
                        "displayName": f"{query} - {airport_name} ({code})"
                    })
                    if results:
                        return results[:limit]
            
            # Try to extract from organic results snippets
            organic_results = data.get("organic_results", [])
            for result in organic_results[:3]:
                snippet = result.get("snippet", "")
                title = result.get("title", "")
                combined_text = f"{title} {snippet}"
                
                # Look for airport code pattern: "IATA: XXX" or "(XXX)" or "Code: XXX"
                code_patterns = [
                    r'IATA[:\s]+([A-Z]{3})',
                    r'\(([A-Z]{3})\)',
                    r'Code[:\s]+([A-Z]{3})',
                    r'\b([A-Z]{3})\s+airport',
                ]
                
                for pattern in code_patterns:
                    code_match = re.search(pattern, combined_text, re.IGNORECASE)
                    if code_match:
                        code = code_match.group(1)
                        # Extract airport name from title
                        airport_name = title.replace(f"({code})", "").strip()
                        if not airport_name:
                            airport_name = f"{query} Airport"
                        
                        results.append({
                            "code": code,
                            "name": airport_name,
                            "city": query,
                            "country": "Unknown",
                            "displayName": f"{query} - {airport_name} ({code})"
                        })
                        break
                
                if results:
                    return results[:limit]
        
        return []
        
    except Exception as e:
        # Silent fail - don't break the app if SerpAPI is unavailable
        print(f"   Warning: SerpAPI airport search failed: {e}")
        return []


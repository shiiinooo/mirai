"""API tools for travel data generation using SerpAPI."""

import os
import re
import requests
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def _extract_airport_code(location: str) -> Optional[str]:
    """
    Try to extract airport code from location string.
    Looks for 3-letter uppercase codes or uses common city mappings.
    """
    if not location:
        return None
    
    # Common city to airport code mappings (check these first)
    city_to_airport = {
        "new york": "JFK",
        "nyc": "JFK",
        "los angeles": "LAX",
        "la": "LAX",
        "chicago": "ORD",
        "san francisco": "SFO",
        "sf": "SFO",
        "miami": "MIA",
        "boston": "BOS",
        "seattle": "SEA",
        "atlanta": "ATL",
        "dallas": "DFW",
        "denver": "DEN",
        "paris": "CDG",
        "london": "LHR",
        "tokyo": "NRT",
        "sydney": "SYD",
        "dubai": "DXB",
        "frankfurt": "FRA",
        "amsterdam": "AMS",
        "madrid": "MAD",
        "rome": "FCO",
        "barcelona": "BCN",
        "berlin": "BER",
        "vienna": "VIE",
        "zurich": "ZRH",
        "munich": "MUC",
        "milan": "MXP",
        "istanbul": "IST",
    }
    
    # Country codes to exclude (not airport codes)
    country_codes = {"USA", "UK", "UAE", "U.S.", "U.S.A."}
    
    location_lower = location.lower().strip()
    
    # Check if it's already an airport code (3 uppercase letters, standalone)
    if len(location.strip()) == 3 and location.strip().isupper() and location.strip().isalpha():
        return location.strip()
    
    # Try city mapping FIRST (before regex to avoid matching country codes)
    for city, code in city_to_airport.items():
        if city in location_lower:
            return code
    
    # Check for airport code in parentheses (e.g., "New York (JFK)")
    paren_match = re.search(r'\(([A-Z]{3})\)', location)
    if paren_match:
        code = paren_match.group(1)
        if code not in country_codes:
            return code
    
    # Check for airport code in the string, but exclude country codes
    code_match = re.search(r'\b([A-Z]{3})\b', location)
    if code_match:
        code = code_match.group(1)
        if code not in country_codes:
            return code
    
    return None


def _search_flights_serpapi(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    *,
    gl: str = "us",
    hl: str = "en",
    currency: str = "EUR",
    adults: int = 1,
    children: int = 0,
    travel_class: int = 1,  # 1=Economy, 2=Business, 3=First, 4=All
    max_price: Optional[int] = None,
    stops: Optional[int] = None,  # Maximum number of stops
    deep_search: bool = True,  # Enable for complete results matching browser
) -> Dict[str, Any]:
    """
    Call SerpAPI Google Flights and return raw JSON.
    
    Args:
        departure_id: Airport code (e.g., "CDG", "JFK")
        arrival_id: Airport code (e.g., "NRT", "LAX")
        outbound_date: Departure date in YYYY-MM-DD format
        return_date: Return date for round trips in YYYY-MM-DD format
        travel_class: 1=Economy, 2=Business, 3=First Class, 4=All (default: 1)
        deep_search: Enable deep search for more complete results (default: True)
    """
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    if not SERPAPI_API_KEY:
        raise RuntimeError("Set SERPAPI_API_KEY env var with your SerpApi key.")
    
    params: Dict[str, Any] = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": currency,
        "hl": hl,
        "gl": gl,
        "adults": adults,
        "children": children,
        "travel_class": travel_class,
        "api_key": SERPAPI_API_KEY,
    }
    
    # Add return date for round trips
    if return_date:
        params["return_date"] = return_date
    
    # Add optional filters
    if max_price is not None:
        params["max_price"] = max_price
    if stops is not None:
        params["stops"] = stops
    if deep_search:
        params["deep_search"] = "true"
    
    url = "https://serpapi.com/search.json"
    resp = requests.get(url, params=params, timeout=30)
    
    if resp.status_code != 200:
        error_detail = resp.text[:500] if resp.text else "No error details"
        raise RuntimeError(f"SerpAPI flights search HTTP error {resp.status_code}: {error_detail}")
    
    resp.raise_for_status()
    data = resp.json()
    
    status = data.get("search_metadata", {}).get("status")
    if status != "Success":
        error_info = data.get("error", "Unknown error")
        raise RuntimeError(f"SerpAPI flights search failed, status={status}, error={error_info}")
    
    return data


def _flatten_flights_serpapi(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flatten SerpAPI Google Flights JSON into a simple list.
    For round trips, splits into separate outbound and return flights.
    """
    options: List[Dict[str, Any]] = []
    
    # Get search parameters to determine origin/destination
    search_params = data.get("search_parameters", {})
    departure_id = search_params.get("departure_id")
    arrival_id = search_params.get("arrival_id")
    is_round_trip = search_params.get("return_date") is not None
    
    for block_name in ["best_flights", "other_flights"]:
        flights_block = data.get(block_name) or []
        for option in flights_block:
            price = option.get("price")
            # Ensure price is a number or None
            if price is not None:
                try:
                    price = float(price)
                except (ValueError, TypeError):
                    price = None
            
            if price is None:
                continue
            
            total_duration = option.get("total_duration")
            f_type = option.get("type", "")
            all_segments = option.get("flights", [])
            
            # Process all segments
            segments = []
            for seg in all_segments:
                dep = seg.get("departure_airport", {})
                arr = seg.get("arrival_airport", {})
                
                segments.append({
                    "from": dep.get("id"),
                    "from_name": dep.get("name"),
                    "dep_time": dep.get("time"),
                    "to": arr.get("id"),
                    "to_name": arr.get("name"),
                    "arr_time": arr.get("time"),
                    "airline": seg.get("airline"),
                    "flight_number": seg.get("flight_number"),
                    "duration_min": seg.get("duration"),
                })
            
            # For round trips, try to split into outbound and return legs
            if is_round_trip and len(segments) > 1 and departure_id and arrival_id:
                # Find where return journey starts (when we fly back towards origin)
                outbound_segments = []
                return_segments = []
                
                for i, seg in enumerate(segments):
                    # Check if this segment is heading back to origin
                    if seg["to"] == departure_id or (return_segments and len(return_segments) > 0):
                        # This is part of return journey
                        return_segments.append(seg)
                    elif seg["from"] == arrival_id and i > 0:
                        # Started from destination, must be return
                        return_segments.append(seg)
                    else:
                        # Still on outbound journey
                        outbound_segments.append(seg)
                
                # If we successfully split, store as a single option with both legs
                if outbound_segments and return_segments:
                    options.append({
                        "price": price,
                        "currency": data.get("search_parameters", {}).get("currency", "EUR"),
                        "type": "Round trip",
                        "total_duration_min": total_duration,
                        "segments": segments,  # Keep all segments
                        "outbound_segments": outbound_segments,
                        "return_segments": return_segments,
                        "link": option.get("link"),
                        "leg": "round_trip",
                        "has_return": True,
                    })
                    continue
            
            # If not round trip or couldn't split, keep as single flight
            options.append({
                "price": price,
                "currency": data.get("search_parameters", {}).get("currency", "EUR"),
                "type": f_type,
                "total_duration_min": total_duration,
                "segments": segments,
                "link": option.get("link"),
                "leg": option.get("leg", "outbound"),
            })
    
    return options


def search_flights(
    origin: Optional[str],
    destination: str,
    travel_dates: Optional[Dict[str, str]],
    constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for flight options using SerpAPI Google Flights.
    Returns flight options with data from SerpAPI, transformed to match expected format.
    
    Falls back to mock data if SerpAPI fails or airport codes cannot be determined.
    """
    # Try to use SerpAPI if we have travel dates and can determine airport codes
    if travel_dates and travel_dates.get("start"):
        try:
            outbound_date = travel_dates["start"]
            # Check for round trip return date (stored in "return" key)
            return_date = travel_dates.get("return") or travel_dates.get("end")
            
            # Extract or get airport codes
            departure_id = None
            arrival_id = None
            
            # Check if airport codes are provided in constraints
            if constraints:
                departure_id = constraints.get("departure_airport_code")
                arrival_id = constraints.get("arrival_airport_code")
            
            # Try to extract from location strings if not provided
            if not departure_id and origin:
                departure_id = _extract_airport_code(origin)
                if departure_id:
                    print(f"   Extracted departure airport code: {departure_id} from '{origin}'")
            if not arrival_id:
                arrival_id = _extract_airport_code(destination)
                if arrival_id:
                    print(f"   Extracted arrival airport code: {arrival_id} from '{destination}'")
            
            # If we have both airport codes, use SerpAPI
            if departure_id and arrival_id:
                print(f"   Using SerpAPI with departure: {departure_id}, arrival: {arrival_id}")
                # Map constraints to SerpAPI parameters
                currency = constraints.get("currency", "EUR") if constraints else "EUR"
                adults = constraints.get("adults", 1) if constraints else 1
                children = constraints.get("children", 0) if constraints else 0
                travel_class = 1  # Economy by default
                max_price = None
                stops = None
                
                if constraints:
                    comfort_level = constraints.get("comfort_level", "mid")
                    # Map comfort level to travel class
                    # Note: Using Economy (1) for better availability and prices
                    if comfort_level == "high":
                        travel_class = 2  # Business
                    elif comfort_level == "mid":
                        travel_class = 1  # Economy (best availability)
                    else:
                        travel_class = 1  # Economy
                    
                    if "max_price" in constraints:
                        max_price = constraints["max_price"]
                    if "max_stops" in constraints:
                        stops = constraints["max_stops"]
                
                # Call SerpAPI with deep_search enabled for complete results
                data = _search_flights_serpapi(
                    departure_id=departure_id,
                    arrival_id=arrival_id,
                    outbound_date=outbound_date,
                    return_date=return_date,
                    currency=currency,
                    adults=adults,
                    children=children,
                    travel_class=travel_class,
                    max_price=max_price,
                    stops=stops,
                    deep_search=True,  # Enable to get results matching browser
                )
                
                # Flatten and transform to expected format
                serpapi_flights = _flatten_flights_serpapi(data)
                
                # Transform to match expected format
                flights = []
                flight_counter = 1
                
                for f in serpapi_flights:
                    segments = f.get("segments", [])
                    if not segments:
                        continue
                    
                    # Determine flight class name
                    travel_class_map = {1: "Economy", 2: "Business", 3: "First Class", 4: "All"}
                    flight_class = travel_class_map.get(travel_class, "Economy")
                    
                    # Safely extract and convert price
                    price_value = f.get("price")
                    if price_value is None:
                        price_value = 0
                    try:
                        price_value = float(price_value) if price_value else 0
                    except (ValueError, TypeError):
                        price_value = 0
                    
                    booking_link = f.get("link")
                    
                    # Keep all flights as single entities (no splitting)
                    # For round trips, this includes both outbound and return in segments
                    if True:  # Process all flights the same way
                        first_segment = segments[0]
                        last_segment = segments[-1]
                        
                        # Calculate duration string
                        total_duration_min = f.get("total_duration_min", 0)
                        duration_hours = total_duration_min // 60
                        duration_mins = total_duration_min % 60
                        duration_str = f"{duration_hours}h {duration_mins}m"
                        
                        if not booking_link:
                            from urllib.parse import quote
                            origin_code = first_segment.get("from", "")
                            dest_code = last_segment.get("to", "")
                            if origin_code and dest_code:
                                booking_link = f"https://www.google.com/travel/flights?q=Flights%20{quote(origin_code)}%20to%20{quote(dest_code)}%20{quote(outbound_date)}"
                        
                        flights.append({
                            "id": f"flight_{flight_counter}",
                            "airline": first_segment.get("airline", "Unknown"),
                            "flight_number": first_segment.get("flight_number", ""),
                            "origin": first_segment.get("from_name") or origin or "Unknown",
                            "destination": last_segment.get("to_name") or destination,
                            "departure_time": first_segment.get("dep_time", ""),
                            "arrival_time": last_segment.get("arr_time", ""),
                            "duration": duration_str,
                            "class": flight_class,
                            "price": round(price_value, 2),
                            "currency": f.get("currency", "EUR"),
                            "stops": len(segments) - 1,
                            "baggage_included": True,
                            "cancellation_policy": "Standard",
                            "segments": segments,
                            "link": booking_link,
                            "leg": f.get("leg", "outbound"),
                            "type": f.get("type", "One way"),
                        })
                        flight_counter += 1
                
                # Sort by price
                flights.sort(key=lambda x: x["price"])
                
                return flights[:20]  # Limit to top 20 results
            else:
                raise ValueError(
                    f"Could not determine airport codes. Origin: {origin}, Destination: {destination}. "
                    "Provide airport codes in constraints (departure_airport_code, arrival_airport_code) "
                    "or use city names that can be mapped (e.g., 'New York', 'Los Angeles', 'Paris')"
                )
                
        except Exception as e:
            raise RuntimeError(f"SerpAPI flight search failed: {e}")
    
    # If no travel dates provided, raise error
    raise ValueError("Travel dates are required for flight search. Provide travel_dates with 'start' date.")


def _search_hotels_serpapi(
    q: str,
    check_in_date: str,
    check_out_date: str,
    *,
    currency: str = "EUR",
    adults: int = 2,
    children: int = 0,
    children_ages: Optional[str] = None,
    sort_by: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    hotel_class: Optional[str] = None,
    rating: Optional[int] = None,
    amenities: Optional[str] = None,
    property_types: Optional[str] = None,
    vacation_rentals: bool = False,
) -> Dict[str, Any]:
    """
    Call SerpAPI Google Hotels and return raw JSON.
    """
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    if not SERPAPI_API_KEY:
        raise RuntimeError("Set SERPAPI_API_KEY env var with your SerpApi key.")
    
    params: Dict[str, Any] = {
        "engine": "google_hotels",
        "q": q,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": currency,
        "adults": adults,
        "children": children,
        "api_key": SERPAPI_API_KEY,
    }
    
    if children_ages is not None:
        params["children_ages"] = children_ages
    if sort_by is not None:
        params["sort_by"] = sort_by
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if hotel_class is not None:
        params["hotel_class"] = hotel_class
    if rating is not None:
        params["rating"] = rating
    if amenities is not None:
        params["amenities"] = amenities
    if property_types is not None:
        params["property_types"] = property_types
    if vacation_rentals:
        params["vacation_rentals"] = "true"
    
    url = "https://serpapi.com/search.json"
    resp = requests.get(url, params=params, timeout=30)
    
    if resp.status_code != 200:
        error_detail = resp.text[:500] if resp.text else "No error details"
        raise RuntimeError(f"SerpAPI hotels search HTTP error {resp.status_code}: {error_detail}")
    
    resp.raise_for_status()
    data = resp.json()
    
    status = data.get("search_metadata", {}).get("status")
    if status != "Success":
        error_info = data.get("error", "Unknown error")
        raise RuntimeError(f"SerpAPI hotels search failed, status={status}, error={error_info}")
    
    return data


def _flatten_hotels_serpapi(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flatten SerpAPI Google Hotels JSON into a simple list.
    """
    currency = data.get("search_parameters", {}).get("currency", "EUR")
    properties = data.get("properties", []) or []
    results: List[Dict[str, Any]] = []
    
    for p in properties:
        rate_per_night = p.get("rate_per_night", {}) or {}
        total_rate = p.get("total_rate", {}) or {}
        gps = p.get("gps_coordinates", {}) or {}
        
        results.append({
            "name": p.get("name"),
            "type": p.get("type"),
            "link": p.get("link"),
            "rating": p.get("overall_rating"),
            "reviews": p.get("reviews"),
            "hotel_class": p.get("extracted_hotel_class") or p.get("hotel_class"),
            "night_price": rate_per_night.get("extracted_lowest"),
            "night_price_str": rate_per_night.get("lowest"),
            "total_price": total_rate.get("extracted_lowest"),
            "total_price_str": total_rate.get("lowest"),
            "currency": currency,
            "amenities": p.get("amenities") or [],
            "location_rating": p.get("location_rating"),
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
            "property_token": p.get("property_token"),
            "serpapi_property_details_link": p.get("serpapi_property_details_link"),
        })
    
    return results


def search_hotels(
    destination: str,
    travel_dates: Optional[Dict[str, str]],
    duration: Optional[int],
    constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for hotel options using SerpAPI Google Hotels.
    Returns hotel options with data from SerpAPI, transformed to match expected format.
    
    Falls back to mock data if SerpAPI fails or is not configured.
    """
    # Try to use SerpAPI if we have travel dates
    if travel_dates and travel_dates.get("start") and travel_dates.get("end"):
        try:
            check_in = travel_dates["start"]
            check_out = travel_dates["end"]
            
            # Map constraints to SerpAPI parameters
            sort_by = None  # 3=lowest price, 8=highest rating, 13=most reviewed
            hotel_class = None
            rating = None
            max_price = None
            
            if constraints:
                comfort_level = constraints.get("comfort_level", "mid")
                
                # Map comfort level to hotel class
                if comfort_level == "high":
                    hotel_class = "4,5"  # 4-5 star hotels
                    rating = 8  # 4.0+ rating
                elif comfort_level == "low":
                    hotel_class = "1,2,3"  # Budget hotels
                    rating = None
                else:
                    hotel_class = "3,4"  # Mid-range
                    rating = 7  # 3.5+ rating
                
                # Budget constraint
                if "max_price" in constraints:
                    max_price = constraints["max_price"]
            
            # Default to sorting by lowest price if no other preference
            if sort_by is None:
                sort_by = 3
            
            # Clean destination for query (remove country if present, just use city)
            # "Paris, France" -> "Paris"
            query_destination = destination.split(",")[0].strip()
            
            # Get traveler counts from constraints
            adults = constraints.get("adults", 2) if constraints else 2
            children = constraints.get("children", 0) if constraints else 0
            currency = constraints.get("currency", "EUR") if constraints else "EUR"
            
            # Generate children_ages if children are specified but ages not provided
            # SerpAPI requires children_ages to match the number of children
            # Default to age 8 for each child (reasonable default for hotel searches)
            children_ages = None
            if children > 0:
                children_ages = constraints.get("children_ages") if constraints else None
                if not children_ages:
                    # Generate default ages: assume all children are 8 years old
                    # Format: comma-separated string like "8,8" for 2 children
                    children_ages = ",".join(["8"] * children)
            
            # Call SerpAPI
            data = _search_hotels_serpapi(
                q=query_destination,
                check_in_date=check_in,
                check_out_date=check_out,
                currency=currency,
                adults=adults,
                children=children,
                children_ages=children_ages,
                sort_by=sort_by,
                max_price=max_price,
                hotel_class=hotel_class,
                rating=rating,
                vacation_rentals=False,
            )
            
            # Flatten and transform to expected format
            serpapi_hotels = _flatten_hotels_serpapi(data)
            
            # Transform to match expected format
            hotels = []
            for i, h in enumerate(serpapi_hotels, start=1):
                # Calculate total price for stay
                nights = duration if duration else 1
                night_price = h.get("night_price") or 0
                total_price = h.get("total_price") or (night_price * nights)
                
                # Map hotel type
                hotel_type = h.get("type", "hotel")
                if hotel_type == "hotel":
                    hotel_type = "Hotel"
                elif hotel_type == "vacation rental":
                    hotel_type = "Apartment"
                
                # Extract amenities list
                amenities_list = h.get("amenities", [])
                if isinstance(amenities_list, list):
                    amenities = [str(a) for a in amenities_list]
                else:
                    amenities = []
                
                # Determine location description
                location_rating = h.get("location_rating")
                if location_rating and location_rating >= 4.5:
                    location = "City Center"
                elif location_rating and location_rating >= 4.0:
                    location = "Downtown"
                else:
                    location = "Near City Center"
                
                hotels.append({
                    "id": f"hotel_{h.get('property_token', i)}",
                    "name": h.get("name", f"Hotel {i}"),
                    "type": hotel_type,
                    "rating": h.get("rating") or 0.0,
                    "reviews": h.get("reviews") or 0,
                    "price_per_night": round(night_price, 2) if night_price else 0.0,
                    "total_price": round(total_price, 2) if total_price else 0.0,
                    "location": location,
                    "distance_to_center": round((5.0 - (location_rating or 3.0)) * 0.5, 1) if location_rating else 2.5,
                    "amenities": amenities[:10],  # Limit to 10 amenities
                    "breakfast_included": "breakfast" in " ".join(amenities).lower(),
                    "cancellation_policy": "Free cancellation",  # Default, SerpAPI doesn't always provide this
                    "link": h.get("link"),
                    "latitude": h.get("latitude"),
                    "longitude": h.get("longitude"),
                })
            
            # Sort by value (rating/price ratio)
            hotels.sort(key=lambda x: x["rating"] / (x["price_per_night"] / 100) if x["price_per_night"] > 0 else 0, reverse=True)
            
            return hotels[:20]  # Limit to top 20 results
            
        except Exception as e:
            raise RuntimeError(f"SerpAPI hotel search failed: {e}")
    
    # If no travel dates provided, raise error
    raise ValueError("Travel dates are required for hotel search. Provide travel_dates with 'start' and 'end' dates.")


def _search_local_serpapi(
    q: str,
    location: str,
    *,
    hl: str = "en",
    gl: str = "us",
    type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call SerpAPI Google Local (Places) and return raw JSON.
    
    Args:
        q: Search query (e.g., "coffee shops", "best restaurants", "Italian restaurant")
        location: Location to search in (e.g., "Paris, France", "New York, NY")
        hl: Host language (default: "en")
        gl: Host country (default: "us")
        type: Place type filter (optional)
    """
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    if not SERPAPI_API_KEY:
        raise RuntimeError("Set SERPAPI_API_KEY env var with your SerpApi key.")
    
    params: Dict[str, Any] = {
        "engine": "google_local",
        "q": q,
        "location": location,
        "hl": hl,
        "gl": gl,
        "api_key": SERPAPI_API_KEY,
    }
    
    if type is not None:
        params["type"] = type
    
    url = "https://serpapi.com/search.json"
    resp = requests.get(url, params=params, timeout=30)
    
    if resp.status_code != 200:
        error_detail = resp.text[:500] if resp.text else "No error details"
        raise RuntimeError(f"SerpAPI local search HTTP error {resp.status_code}: {error_detail}")
    
    resp.raise_for_status()
    data = resp.json()
    
    status = data.get("search_metadata", {}).get("status")
    if status != "Success":
        error_info = data.get("error", "Unknown error")
        raise RuntimeError(f"SerpAPI local search failed, status={status}, error={error_info}")
    
    return data


def _search_events_serpapi(
    q: str,
    *,
    hl: str = "en",
    gl: str = "us",
    htichips: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call SerpAPI Google Events and return raw JSON.
    
    Args:
        q: Search query (e.g., "Events in Paris", "concerts in New York")
        hl: Host language (default: "en")
        gl: Host country (default: "us")
        htichips: Filters (e.g., "date:today", "event_type:Virtual-Event")
    """
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    if not SERPAPI_API_KEY:
        raise RuntimeError("Set SERPAPI_API_KEY env var with your SerpApi key.")
    
    params: Dict[str, Any] = {
        "engine": "google_events",
        "q": q,
        "hl": hl,
        "gl": gl,
        "api_key": SERPAPI_API_KEY,
    }
    
    if htichips is not None:
        params["htichips"] = htichips
    
    url = "https://serpapi.com/search.json"
    resp = requests.get(url, params=params, timeout=30)
    
    if resp.status_code != 200:
        error_detail = resp.text[:500] if resp.text else "No error details"
        raise RuntimeError(f"SerpAPI events search HTTP error {resp.status_code}: {error_detail}")
    
    resp.raise_for_status()
    data = resp.json()
    
    status = data.get("search_metadata", {}).get("status")
    if status != "Success":
        error_info = data.get("error", "Unknown error")
        raise RuntimeError(f"SerpAPI events search failed, status={status}, error={error_info}")
    
    return data


def search_restaurants(
    destination: str,
    preferred_activities: List[str],
    constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for restaurants and coffee shops using SerpAPI Google Local.
    Returns dining options based on preferences and constraints.
    
    Uses dynamic API calls to get real restaurant and coffee shop data.
    """
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    if not SERPAPI_API_KEY:
        raise RuntimeError("Set SERPAPI_API_KEY env var to use restaurant search.")
    
    try:
        # Clean destination for query
        print("--------------------------------")
        query_location = destination.split(",")[0].strip() if "," in destination else destination
        
        # Extract cuisine preferences from preferred_activities
        cuisine_keywords = []
        for activity in preferred_activities:
            activity_lower = activity.lower()
            if any(word in activity_lower for word in ["food", "cuisine", "dining", "restaurant"]):
                cuisine_keywords.append(activity)
        
        # Determine search queries based on preferences
        search_queries = []
        
        # Always include best restaurants
        search_queries.append(f"Best restaurants in {query_location}")
        
        # Add coffee shops if not explicitly excluded
        search_queries.append(f"Coffee shops in {query_location}")
        
        # Add cuisine-specific searches if preferences exist
        if cuisine_keywords:
            for cuisine in cuisine_keywords[:2]:  # Limit to 2 cuisine types
                search_queries.append(f"{cuisine} in {query_location}")
        
        all_dining_results = []
        
        # Perform searches
        # Use city name only for location - SerpAPI doesn't accept "City, Country" format
        location_for_api = query_location  # Already extracted city name above
        
        for query in search_queries:
            try:
                data = _search_local_serpapi(
                    q=query,
                    location=location_for_api,
                    hl="en",
                    gl="us"
                )
                
                # Extract local results
                local_results = data.get("local_results", {})
                places = local_results.get("places", []) if isinstance(local_results, dict) else local_results
                
                for place in places:
                    # Extract price level
                    price_str = place.get("price", "$")
                    price_level = price_str if price_str else "$$"
                    
                    # Calculate average cost based on price level
                    price_mapping = {"$": 15, "$$": 30, "$$$": 60, "$$$$": 100}
                    avg_cost = price_mapping.get(price_level, 30)
                    
                    # Extract description or type
                    place_type = place.get("type", "Restaurant")
                    description = place.get("description", "")
                    
                    # Determine meal types
                    meal_types = []
                    if "coffee" in place_type.lower() or "coffee" in description.lower():
                        meal_types = ["Breakfast", "Lunch"]
                    else:
                        meal_types = ["Lunch", "Dinner"]
                    
                    # Determine cuisine type from type or description
                    cuisine = "Local Cuisine"
                    if place_type and place_type != "Restaurant":
                        cuisine = place_type
                    
                    # Extract location info
                    address = place.get("address", "")
                    gps = place.get("gps_coordinates", {})
                    
                    # Determine reservations requirement
                    rating = place.get("rating", 0)
                    reviews = place.get("reviews", 0)
                    reservations = "Recommended" if rating >= 4.5 and reviews > 100 else "Walk-in"
                    
                    all_dining_results.append({
                        "id": f"restaurant_{place.get('place_id', len(all_dining_results)+1)}",
                        "name": place.get("title", "Restaurant"),
                        "cuisine": cuisine,
                        "rating": rating,
                        "reviews": reviews,
                        "price_level": price_level,
                        "avg_cost_per_person": avg_cost,
                        "meal_types": meal_types,
                        "location": address or "City Center",
                        "distance_to_center": 0.0,  # SerpAPI doesn't always provide this
                        "reservations": reservations,
                        "dietary_options": [],  # Would need more detailed data
                        "ambiance": "Casual",  # Would need more detailed data
                        "specialties": [description] if description else [],
                        "link": place.get("links", {}).get("website") if place.get("links") else None,
                        "phone": place.get("phone"),
                        "latitude": gps.get("latitude"),
                        "longitude": gps.get("longitude"),
                    })
                    
            except Exception as e:
                print(f"   Warning: Failed to search '{query}': {e}")
                continue
        
        # Remove duplicates based on name
        seen_names = set()
        unique_results = []
        for result in all_dining_results:
            if result["name"] not in seen_names:
                seen_names.add(result["name"])
                unique_results.append(result)
        
        # Sort by rating and value
        unique_results.sort(key=lambda x: (x["rating"], -x["avg_cost_per_person"]), reverse=True)
        
        # Apply budget constraints if provided
        if constraints and "max_daily_food_budget" in constraints:
            max_budget = constraints["max_daily_food_budget"]
            unique_results = [r for r in unique_results if r["avg_cost_per_person"] <= max_budget]
        
        return unique_results[:20]  # Limit to top 20 results
        
    except Exception as e:
        raise RuntimeError(f"SerpAPI restaurant search failed: {e}")


def search_activities(
    destination: str,
    preferred_activities: List[str],
    duration: Optional[int],
    constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for tourist activities and attractions using SerpAPI Google Local and Google Events.
    Returns activities based on user preferences and constraints.
    
    Uses dynamic API calls to get real tourist activities, events, and attractions.
    """
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    if not SERPAPI_API_KEY:
        raise RuntimeError("Set SERPAPI_API_KEY env var to use activities search.")
    
    try:
        # Clean destination for query
        query_location = destination.split(",")[0].strip() if "," in destination else destination
        
        # Build search queries based on preferences
        search_queries = []
        
        # Always include top attractions
        search_queries.append(f"Top attractions in {query_location}")
        search_queries.append(f"Things to do in {query_location}")
        
        # Add preference-specific searches
        activity_mapping = {
            "museums": "museums",
            "culture": "cultural sites",
            "nightlife": "nightlife",
            "adventure": "adventure activities",
            "outdoor": "outdoor activities",
            "hiking": "hiking trails",
            "shopping": "shopping",
            "art": "art galleries",
            "history": "historical sites",
            "nature": "nature parks",
        }
        
        for pref in preferred_activities:
            pref_lower = pref.lower()
            for key, value in activity_mapping.items():
                if key in pref_lower:
                    search_queries.append(f"{value} in {query_location}")
                    break
        
        all_activities = []
        
        # Search Google Local for attractions
        for query in search_queries[:5]:  # Limit to 5 queries
            try:
                data = _search_local_serpapi(
                    q=query,
                    location=destination,
                    hl="en",
                    gl="us"
                )
                
                # Extract local results
                local_results = data.get("local_results", {})
                places = local_results.get("places", []) if isinstance(local_results, dict) else local_results
                
                for place in places:
                    # Determine activity type
                    place_type = place.get("type", "Attraction")
                    
                    # Estimate duration based on type
                    duration_map = {
                        "museum": "2-3 hours",
                        "park": "1-2 hours",
                        "tour": "3-4 hours",
                        "landmark": "1 hour",
                        "attraction": "2 hours",
                    }
                    
                    estimated_duration = "2 hours"
                    for key, dur in duration_map.items():
                        if key in place_type.lower():
                            estimated_duration = dur
                            break
                    
                    # Estimate price (many attractions are free or low cost)
                    price = 0
                    if "tour" in place_type.lower():
                        price = 35
                    elif "museum" in place_type.lower():
                        price = 20
                    
                    # Extract location info
                    address = place.get("address", "")
                    gps = place.get("gps_coordinates", {})
                    
                    all_activities.append({
                        "id": f"activity_{place.get('place_id', len(all_activities)+1)}",
                        "name": place.get("title", "Activity"),
                        "type": place_type,
                        "duration": estimated_duration,
                        "price": price,
                        "rating": place.get("rating", 0),
                        "reviews": place.get("reviews", 0),
                        "location": address or "City Center",
                        "best_time": "Any time",
                        "booking_required": price > 0,
                        "description": place.get("description", ""),
                        "link": place.get("links", {}).get("website") if place.get("links") else None,
                        "latitude": gps.get("latitude"),
                        "longitude": gps.get("longitude"),
                    })
                    
            except Exception as e:
                print(f"   Warning: Failed to search activities '{query}': {e}")
                continue
        
        # Search Google Events for events and activities
        try:
            events_data = _search_events_serpapi(
                q=f"Events in {query_location}",
                hl="en",
                gl="us"
            )
            
            events_results = events_data.get("events_results", [])
            
            for event in events_results[:10]:  # Limit to 10 events
                # Extract event details
                date_info = event.get("date", {})
                when = date_info.get("when", "Check event page")
                
                # Extract address
                address_list = event.get("address", [])
                address = ", ".join(address_list) if isinstance(address_list, list) else str(address_list)
                
                # Extract venue info
                venue = event.get("venue", {})
                venue_name = venue.get("name", "")
                venue_rating = venue.get("rating", 0)
                
                # Determine if tickets are required
                ticket_info = event.get("ticket_info", [])
                has_tickets = len(ticket_info) > 0
                
                all_activities.append({
                    "id": f"event_{len(all_activities)+1}",
                    "name": event.get("title", "Event"),
                    "type": "Event",
                    "duration": "2-3 hours",
                    "price": 0,  # Price info not always available
                    "rating": venue_rating if venue_rating else 4.0,
                    "reviews": venue.get("reviews", 0) if venue else 0,
                    "location": address or venue_name or "City Center",
                    "best_time": when,
                    "booking_required": has_tickets,
                    "description": event.get("description", ""),
                    "link": event.get("link"),
                    "thumbnail": event.get("thumbnail"),
                })
                
        except Exception as e:
            print(f"   Warning: Failed to search events: {e}")
        
        # Remove duplicates based on name
        seen_names = set()
        unique_activities = []
        for activity in all_activities:
            if activity["name"] not in seen_names:
                seen_names.add(activity["name"])
                unique_activities.append(activity)
        
        # Sort by rating
        unique_activities.sort(key=lambda x: x["rating"], reverse=True)
        
        # Apply budget constraints if provided
        if constraints and "max_activity_price" in constraints:
            max_price = constraints["max_activity_price"]
            unique_activities = [a for a in unique_activities if a["price"] <= max_price]
        
        return unique_activities[:25]  # Limit to top 25 results
        
    except Exception as e:
        raise RuntimeError(f"SerpAPI activities search failed: {e}")


def estimate_costs(
    transport,  # Can be Dict, List[Dict], or None
    accommodation: Optional[Dict[str, Any]],
    activities: List[Dict[str, Any]],
    restaurants: List[Dict[str, Any]],
    duration: int,
    num_travelers: int = 1
) -> Dict[str, float]:
    """
    Calculate estimated costs for the trip.
    
    Args:
        transport: Selected transport option (single flight or list for round trip)
        accommodation: Selected accommodation
        activities: List of selected activities
        restaurants: List of selected restaurants
        duration: Trip duration in days
        num_travelers: Number of travelers (adults + children)
    
    Returns:
        Dictionary with cost breakdown
    """
    # Calculate transport cost (handle both single flight and round trip)
    # Transport prices from API are typically per person, so multiply by travelers
    transport_cost = 0
    if transport:
        if isinstance(transport, list):
            # Round trip with multiple flights
            transport_cost = sum(flight.get("price", 0) for flight in transport) * num_travelers
        else:
            # Single flight
            transport_cost = transport.get("price", 0) * num_travelers
    
    # Accommodation total_price is typically for the room, not per person
    accommodation_cost = accommodation["total_price"] if accommodation else 0
    
    # Activities might be per person or per group - assume per person for now
    activities_cost = sum(act.get("price", 0) for act in activities) * num_travelers
    
    # Dining is per person, so multiply by travelers
    dining_cost = sum(rest.get("avg_cost_per_person", 0) for rest in restaurants) * num_travelers
    
    # Miscellaneous expenses per person per day
    miscellaneous_cost = duration * 20 * num_travelers
    
    costs = {
        "transport": transport_cost,
        "accommodation": accommodation_cost,
        "activities": activities_cost,
        "dining": dining_cost,
        "miscellaneous": miscellaneous_cost
    }
    
    costs["total"] = sum(costs.values())
    
    return costs

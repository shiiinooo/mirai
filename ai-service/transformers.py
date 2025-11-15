"""
Data transformation utilities for converting between frontend and AI service formats.

This module handles:
1. Request transformation: Frontend TripPlanRequest → AI service state
2. Response transformation: AI service result → Frontend Trip format
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid


def transform_request_to_state(request) -> Dict[str, Any]:
    """
    Transform frontend TripPlanRequest to AI service initial state format.
    
    Args:
        request: TripPlanRequest from frontend
        
    Returns:
        Dictionary containing initial state for the AI service graph
    """
    # Parse dates and calculate duration
    start_date = datetime.fromisoformat(request.startDate)
    end_date = datetime.fromisoformat(request.endDate)
    duration = (end_date - start_date).days + 1
    
    # Map comfort level to constraints
    comfort_mapping = {
        "backpacker": "low",
        "standard": "mid",
        "premium": "high"
    }
    
    # Map travel pace to walking distance (rough approximation)
    pace_to_distance = {
        "chill": 3,      # 3km per day
        "balanced": 5,   # 5km per day
        "packed": 8      # 8km per day
    }
    
    # Build constraints with traveler information
    constraints = {
        "comfort_level": comfort_mapping.get(request.comfortLevel, "mid"),
        "walking_distance": pace_to_distance.get(request.travelPace, 5),
        "allergies": [],  # Can be extended if frontend adds this field
        # Add airport codes if provided
        "departure_airport_code": getattr(request, "originAirportCode", None),
        "arrival_airport_code": getattr(request, "destinationAirportCode", None),
        # Add traveler counts for flight and hotel searches
        "adults": getattr(request, "adults", 1),
        "children": getattr(request, "children", 0),
        "currency": getattr(request, "currency", "EUR"),
    }
    
    # Build travel dates with round trip support
    travel_dates = {
        "start": request.startDate,
        "end": request.endDate
    }
    if getattr(request, "roundTrip", False) and getattr(request, "returnDate", None):
        travel_dates["return"] = request.returnDate
    
    # Build initial state
    initial_state = {
        "destination": request.destination,
        "origin": request.origin,  # Get origin from frontend request
        "travel_dates": travel_dates,
        "duration": duration,
        "budget": request.totalBudget,
        "preferred_activities": request.preferredActivities,
        "constraints": constraints,
        # Initialize empty lists/values
        "transport_options": [],
        "accommodation_options": [],
        "activities_options": [],
        "dining_options": [],
        "key_phrases": None,
        "activity_stories": {},
        "selected_transport": None,
        "selected_accommodation": None,
        "selected_activities": [],
        "selected_restaurants": [],
        "total_cost": 0.0,
        "remaining_budget": request.totalBudget,
        "cost_breakdown": {},
        "requires_adjustment": False,
        "adjustment_iteration": 0,
        "max_iterations": 2,
        "final_itinerary": None,
        "messages": []
    }
    
    return initial_state


def transform_result_to_trip(result: Dict[str, Any], request) -> Dict[str, Any]:
    """
    Transform AI service result to frontend Trip format.
    
    Args:
        result: Output from AI service graph
        request: Original TripPlanRequest (for metadata)
        
    Returns:
        Dictionary in Trip format expected by frontend
    """
    # Generate unique trip ID
    trip_id = str(uuid.uuid4())
    
    # Parse dates
    start_date = datetime.fromisoformat(request.startDate)
    end_date = datetime.fromisoformat(request.endDate)
    duration = (end_date - start_date).days + 1
    
    # Get final itinerary from result
    final_itinerary = result.get("final_itinerary", {})
    itinerary_list = final_itinerary.get("itinerary", [])
    
    # If itinerary is empty but we have selected activities, create a basic itinerary
    if not itinerary_list and final_itinerary.get("selected_activities"):
        print(f"[TRANSFORMER] Itinerary empty, creating basic itinerary from {len(final_itinerary.get('selected_activities', []))} activities")
        itinerary_list = []
        activity_idx = 0
        restaurant_idx = 0
        selected_activities = final_itinerary.get("selected_activities", [])
        selected_restaurants = final_itinerary.get("selected_restaurants", [])
        
        for day_num in range(1, duration + 1):
            day_plan = {"day": day_num}
            
            if activity_idx < len(selected_activities):
                activity = selected_activities[activity_idx]
                day_plan["morning"] = {
                    "time": "9:00 AM",
                    "activity": activity.get("name", "Activity"),
                    "description": activity.get("description", activity.get("snippet", "")),
                    "estimated_cost": activity.get("price", activity.get("cost", 0))
                }
                activity_idx += 1
            
            if restaurant_idx < len(selected_restaurants):
                restaurant = selected_restaurants[restaurant_idx]
                day_plan["lunch"] = {
                    "time": "12:30 PM",
                    "restaurant": restaurant.get("name", "Restaurant"),
                    "cuisine": restaurant.get("cuisine", "Local"),
                    "estimated_cost": restaurant.get("avg_cost_per_person", restaurant.get("price", 0))
                }
                restaurant_idx += 1
            
            if activity_idx < len(selected_activities):
                activity = selected_activities[activity_idx]
                day_plan["afternoon"] = {
                    "time": "2:00 PM",
                    "activity": activity.get("name", "Activity"),
                    "description": activity.get("description", activity.get("snippet", "")),
                    "estimated_cost": activity.get("price", activity.get("cost", 0))
                }
                activity_idx += 1
            
            if restaurant_idx < len(selected_restaurants):
                restaurant = selected_restaurants[restaurant_idx]
                day_plan["dinner"] = {
                    "time": "7:00 PM",
                    "restaurant": restaurant.get("name", "Restaurant"),
                    "cuisine": restaurant.get("cuisine", "Local"),
                    "estimated_cost": restaurant.get("avg_cost_per_person", restaurant.get("price", 0))
                }
                restaurant_idx += 1
            
            itinerary_list.append(day_plan)
    
    # Get activity stories from result
    activity_stories = result.get("activity_stories", {})
    
    # Transform daily itinerary to frontend format
    days = transform_daily_itinerary(
        itinerary_list,
        start_date,
        duration,
        request.destination,
        activity_stories=activity_stories,
        selected_activities=final_itinerary.get("selected_activities", [])
    )
    
    # Transform budget information
    budget = transform_budget_data(
        final_itinerary.get("cost_breakdown", {}),
        request.totalBudget,
        request.currency,
        duration
    )
    
    # Generate essentials section (use key_phrases from result if available)
    essentials = generate_essentials(
        request.destination,
        final_itinerary.get("key_phrases")
    )
    
    # Generate logistics section
    logistics = generate_logistics(
        request.destination,
        final_itinerary.get("accommodation", {}),
        final_itinerary.get("transport", {})
    )
    
    # Transform flights (selected transport)
    # For round trips with separate segments, split them for display
    flights = []
    selected_transport = final_itinerary.get("transport")
    
    if selected_transport:
        # Handle case where selected_transport might be a list or single flight
        transport_list = selected_transport if isinstance(selected_transport, list) else [selected_transport]
        
        for idx, transport in enumerate(transport_list):
            if not transport:
                continue
            
            # Check if this is a round trip with both outbound and return segments
            has_outbound = transport.get("outbound_segments")
            has_return = transport.get("return_segments")
            
            if has_outbound and has_return:
                # Split into two flights for display
                outbound_segs = transport.get("outbound_segments", [])
                return_segs = transport.get("return_segments", [])
                
                # Outbound flight
                if outbound_segs:
                    first_seg = outbound_segs[0]
                    last_seg = outbound_segs[-1]
                    outbound_duration = sum(seg.get("duration_min", 0) for seg in outbound_segs)
                    duration_hours = outbound_duration // 60
                    duration_mins = outbound_duration % 60
                    
                    flights.append({
                        "id": f"{transport.get('id', f'flight_{idx}')}_outbound",
                        "airline": first_seg.get("airline", transport.get("airline", "Unknown")),
                        "flight_number": first_seg.get("flight_number", transport.get("flight_number", "")),
                        "origin": first_seg.get("from_name", transport.get("origin", "")),
                        "destination": last_seg.get("to_name", transport.get("destination", "")),
                        "departure_time": first_seg.get("dep_time", ""),
                        "arrival_time": last_seg.get("arr_time", ""),
                        "duration": f"{duration_hours}h {duration_mins}m",
                        "class": transport.get("class", "Economy"),
                        "price": transport.get("price", 0),  # Full price on outbound
                        "currency": transport.get("currency", request.currency),
                        "stops": len(outbound_segs) - 1,
                        "baggage_included": transport.get("baggage_included", True),
                        "cancellation_policy": transport.get("cancellation_policy", "Standard"),
                        "segments": outbound_segs,
                        "link": transport.get("link"),
                        "leg": "outbound",
                        "type": "Round trip",
                    })
                
                # Return flight
                if return_segs:
                    first_seg = return_segs[0]
                    last_seg = return_segs[-1]
                    return_duration = sum(seg.get("duration_min", 0) for seg in return_segs)
                    duration_hours = return_duration // 60
                    duration_mins = return_duration % 60
                    
                    flights.append({
                        "id": f"{transport.get('id', f'flight_{idx}')}_return",
                        "airline": first_seg.get("airline", transport.get("airline", "Unknown")),
                        "flight_number": first_seg.get("flight_number", transport.get("flight_number", "")),
                        "origin": first_seg.get("from_name", ""),
                        "destination": last_seg.get("to_name", ""),
                        "departure_time": first_seg.get("dep_time", ""),
                        "arrival_time": last_seg.get("arr_time", ""),
                        "duration": f"{duration_hours}h {duration_mins}m",
                        "class": transport.get("class", "Economy"),
                        "price": 0,  # Price already counted in outbound
                        "currency": transport.get("currency", request.currency),
                        "stops": len(return_segs) - 1,
                        "baggage_included": transport.get("baggage_included", True),
                        "cancellation_policy": transport.get("cancellation_policy", "Standard"),
                        "segments": return_segs,
                        "link": transport.get("link"),
                        "leg": "return",
                        "type": "Round trip",
                    })
            else:
                # Single flight or one-way
                flight = {
                    "id": transport.get("id", f"flight_{idx + 1}"),
                    "airline": transport.get("airline", "Unknown"),
                    "flight_number": transport.get("flight_number", ""),
                    "origin": transport.get("origin", ""),
                    "destination": transport.get("destination", ""),
                    "departure_time": transport.get("departure_time", ""),
                    "arrival_time": transport.get("arrival_time", ""),
                    "duration": transport.get("duration", ""),
                    "class": transport.get("class", "Economy"),
                    "price": transport.get("price", 0),
                    "currency": transport.get("currency", request.currency),
                    "stops": transport.get("stops", 0),
                    "baggage_included": transport.get("baggage_included", True),
                    "cancellation_policy": transport.get("cancellation_policy", "Standard"),
                    "segments": transport.get("segments", []),
                    "link": transport.get("link"),
                    "leg": transport.get("leg", "outbound"),
                    "type": transport.get("type", "One way"),
                }
                flights.append(flight)
    
    # Transform selected activities (all 10 activities selected by LLM)
    selected_activities = result.get("selected_activities", [])
    activities_list = []
    
    for activity in selected_activities:
        activities_list.append({
            "id": activity.get("id", ""),
            "name": activity.get("name", ""),
            "description": activity.get("description", activity.get("snippet", "")),
            "type": activity.get("type", ""),
            "duration": activity.get("duration", ""),
            "price": activity.get("price", activity.get("cost", 0)),
            "rating": activity.get("rating", 0),
            "reviews": activity.get("reviews", activity.get("reviews_count", 0)),
            "location": activity.get("location", activity.get("address", "")),
            "best_time": activity.get("best_time", ""),
            "booking_required": activity.get("booking_required", False),
            "link": activity.get("link", activity.get("website", "")),
            "category": activity.get("category", "culture"),
            "tags": activity.get("tags", [])
        })
    
    # Build Trip object
    trip = {
        "id": trip_id,
        "destination": request.destination,
        "startDate": request.startDate,
        "endDate": request.endDate,
        "adults": getattr(request, "adults", 1),
        "children": getattr(request, "children", 0),
        "days": days,
        "budget": budget,
        "essentials": essentials,
        "logistics": logistics,
        "flights": flights if flights else None,
        "activities": activities_list,  # All 10 selected activities
        "createdAt": datetime.utcnow().isoformat()
    }
    
    return trip


def transform_daily_itinerary(
    itinerary: List[Dict], 
    start_date: datetime, 
    duration: int, 
    destination: str,
    activity_stories: Dict[str, str] = None,
    selected_activities: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Transform AI service daily itinerary to frontend days format.
    
    Args:
        itinerary: List of daily plans from AI service
        start_date: Trip start date
        duration: Number of days
        destination: Destination name
        
    Returns:
        List of Day objects for frontend
    """
    days = []
    
    for i in range(duration):
        current_date = start_date + timedelta(days=i)
        day_number = i + 1
        
        # Find matching day in itinerary
        day_plan = None
        for plan in itinerary:
            if plan.get("day") == day_number:
                day_plan = plan
                break
        
        if day_plan:
            # Extract activities for each time slot
            schedule = {
                "morning": extract_activities_for_slot(day_plan, "morning", activity_stories, selected_activities),
                "afternoon": extract_activities_for_slot(day_plan, "afternoon", activity_stories, selected_activities),
                "evening": extract_activities_for_slot(day_plan, "evening", activity_stories, selected_activities)
            }
            
            title = f"Day {day_number} in {destination}"
            description = get_day_description(day_plan)
        else:
            # Generate placeholder if no plan exists
            schedule = {
                "morning": [],
                "afternoon": [],
                "evening": []
            }
            title = f"Day {day_number}"
            description = f"Explore {destination}"
        
        day = {
            "id": f"day-{day_number}",
            "dayNumber": day_number,
            "date": current_date.strftime("%Y-%m-%d"),
            "title": title,
            "description": description,
            "schedule": schedule,
            "travelTip": generate_travel_tip(day_number, destination)
        }
        
        days.append(day)
    
    return days


def extract_activities_for_slot(
    day_plan: Dict, 
    slot_name: str,
    activity_stories: Dict[str, str] = None,
    selected_activities: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Extract and format activities for a specific time slot."""
    activities = []
    activity_stories = activity_stories or {}
    selected_activities = selected_activities or []
    
    # Check for various slot names (morning, lunch, afternoon, dinner, evening)
    slot_data = day_plan.get(slot_name, {})
    
    if not slot_data:
        return activities
    
    # Handle restaurant slots (lunch, dinner)
    if "restaurant" in slot_data:
        activity = {
            "id": f"act-{day_plan.get('day', 0)}-{slot_name}",
            "name": slot_data.get("restaurant", "Meal"),
            "description": f"Enjoy {slot_data.get('cuisine', 'local')} cuisine",
            "time": slot_data.get("time", ""),
            "duration": "1 hour",
            "cost": slot_data.get("estimated_cost", 0),
            "category": "food",
            "tags": []
        }
        activities.append(activity)
    
    # Handle activity slots
    elif "activity" in slot_data:
        activity_name = slot_data.get("activity", "Activity")
        
        # Try to find matching activity in selected_activities by name
        # Use fuzzy matching to handle slight name variations
        matching_activity = None
        matching_activity_id = None
        
        # Normalize activity name for comparison (lowercase, strip whitespace)
        normalized_activity_name = activity_name.lower().strip()
        
        for selected_activity in selected_activities:
            selected_name = selected_activity.get("name", "").lower().strip()
            # Exact match
            if selected_name == normalized_activity_name:
                matching_activity = selected_activity
                matching_activity_id = selected_activity.get("id", "")
                break
            # Partial match (activity name contains selected name or vice versa)
            elif normalized_activity_name in selected_name or selected_name in normalized_activity_name:
                matching_activity = selected_activity
                matching_activity_id = selected_activity.get("id", "")
                # Don't break - continue to look for exact match
                # But if we find one, use it
                if len(selected_name) == len(normalized_activity_name):
                    break
        
        activity = {
            "id": f"act-{day_plan.get('day', 0)}-{slot_name}",
            "name": activity_name,
            "description": slot_data.get("description", ""),
            "time": slot_data.get("time", ""),
            "duration": slot_data.get("duration", "2 hours"),
            "cost": slot_data.get("estimated_cost", 0),
            "category": "culture",
            "tags": []
        }
        
        # Attach story for audio playback (but don't display the text)
        # Use the original activity ID to look up the story
        story = None
        story_activity_id = None
        
        if matching_activity_id and activity_stories:
            # Try to get story by activity ID (preferred method)
            story = activity_stories.get(matching_activity_id)
            if story:
                story_activity_id = matching_activity_id
        
        # Fallback: If story not found by ID, try to find it by searching through all activities
        # This handles cases where activity name doesn't match exactly
        if not story and activity_stories and selected_activities:
            # Try to find story by searching for similar activity names
            normalized_search_name = normalized_activity_name
            for selected_activity in selected_activities:
                selected_name = selected_activity.get("name", "").lower().strip()
                # Check if names are similar (one contains the other)
                if (normalized_search_name in selected_name or selected_name in normalized_search_name) and len(selected_name) > 3:
                    potential_id = selected_activity.get("id", "")
                    if potential_id and potential_id in activity_stories:
                        story = activity_stories.get(potential_id)
                        story_activity_id = potential_id
                        break
        
        # Last resort: Try to find story by iterating through all activity_stories
        # and matching by name (in case ID structure is different)
        if not story and activity_stories:
            # This is a fallback - try to match by finding activities with similar names
            # and checking if their stories exist
            for story_id, story_text in activity_stories.items():
                # Try to find the activity that has this story ID
                for selected_activity in selected_activities:
                    if selected_activity.get("id") == story_id:
                        selected_name = selected_activity.get("name", "").lower().strip()
                        # If names match, use this story
                        if (normalized_activity_name in selected_name or selected_name in normalized_activity_name):
                            story = story_text
                            story_activity_id = story_id
                            break
                if story:
                    break
        
        # Attach story if found
        if story and story_activity_id:
            activity["story"] = story
            # Also store the original activity ID for audio API lookup
            activity["original_activity_id"] = story_activity_id
        else:
            # Debug logging to help diagnose missing stories
            if activity_stories:
                print(f"   [DEBUG] Story not found for '{activity_name}'")
                print(f"   [DEBUG] Matched activity ID: {matching_activity_id}")
                print(f"   [DEBUG] Total stories available: {len(activity_stories)}")
                print(f"   [DEBUG] Sample story IDs: {list(activity_stories.keys())[:3]}")
        
        activities.append(activity)
    
    return activities


def get_day_description(day_plan: Dict) -> str:
    """Generate a description for the day based on activities."""
    activities = []
    
    for slot in ["morning", "lunch", "afternoon", "dinner", "evening"]:
        slot_data = day_plan.get(slot, {})
        if "activity" in slot_data:
            activities.append(slot_data["activity"])
        elif "restaurant" in slot_data:
            activities.append(slot_data["restaurant"])
    
    if activities:
        return f"Explore and enjoy: {', '.join(activities[:3])}"
    return "A day of exploration and adventure"


def generate_travel_tip(day_number: int, destination: str) -> str:
    """Generate a contextual travel tip for the day."""
    tips = [
        f"Start your day early to make the most of your time in {destination}.",
        "Book popular attractions in advance to avoid long queues.",
        "Try local transportation to experience the city like a local.",
        "Don't forget to stay hydrated and take breaks between activities.",
        "Keep some local currency handy for small purchases and tips.",
        "Take time to wander and discover hidden gems off the main tourist path.",
        "Sample street food for an authentic taste of local cuisine.",
        "Charge your devices overnight to capture all your memories."
    ]
    
    return tips[(day_number - 1) % len(tips)]


def transform_budget_data(cost_breakdown: Dict, total_budget: float, currency: str, duration: int) -> Dict[str, Any]:
    """
    Transform cost breakdown to frontend budget format.
    
    Args:
        cost_breakdown: Cost breakdown from AI service
        total_budget: Total budget from request
        currency: Currency code
        duration: Trip duration in days
        
    Returns:
        Budget object for frontend
    """
    # Calculate total from breakdown
    estimated_spend = cost_breakdown.get("total", 0)
    
    # Create categories with breakdowns
    categories = []
    
    # Accommodation
    if cost_breakdown.get("accommodation", 0) > 0:
        categories.append({
            "category": "accommodation",
            "estimated": cost_breakdown["accommodation"],
            "breakdown": [
                {"item": f"Hotel ({duration} nights)", "cost": cost_breakdown["accommodation"]}
            ]
        })
    
    # Food/Dining
    if cost_breakdown.get("dining", 0) > 0:
        categories.append({
            "category": "food",
            "estimated": cost_breakdown["dining"],
            "breakdown": [
                {"item": "Meals & restaurants", "cost": cost_breakdown["dining"]}
            ]
        })
    
    # Transport
    if cost_breakdown.get("transport", 0) > 0:
        categories.append({
            "category": "transport",
            "estimated": cost_breakdown["transport"],
            "breakdown": [
                {"item": "Flights & local transport", "cost": cost_breakdown["transport"]}
            ]
        })
    
    # Activities
    if cost_breakdown.get("activities", 0) > 0:
        categories.append({
            "category": "activities",
            "estimated": cost_breakdown["activities"],
            "breakdown": [
                {"item": "Tours & attractions", "cost": cost_breakdown["activities"]}
            ]
        })
    
    # Miscellaneous
    misc_cost = cost_breakdown.get("miscellaneous", max(0, total_budget * 0.1))
    categories.append({
        "category": "miscellaneous",
        "estimated": misc_cost,
        "breakdown": [
            {"item": "Shopping & extras", "cost": misc_cost * 0.7},
            {"item": "Emergency fund", "cost": misc_cost * 0.3}
        ]
    })
    
    # Recalculate estimated spend
    estimated_spend = sum(cat["estimated"] for cat in categories)
    
    budget = {
        "totalBudget": total_budget,
        "estimatedSpend": estimated_spend,
        "currency": currency,
        "dailyAverage": estimated_spend / duration if duration > 0 else 0,
        "categories": categories
    }
    
    return budget


def generate_essentials(destination: str, key_phrases_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate travel essentials section.
    
    Args:
        destination: Destination name
        key_phrases_data: Key phrases data from AI service (optional)
        
    Returns:
        Essentials object with phrases, tips, advice, etc.
    """
    # Transform key phrases from AI service format to frontend format
    key_phrases = []
    
    if key_phrases_data and key_phrases_data.get("phrases"):
        # Transform from AI service format: {english, translation, phonetic}
        # to frontend format: {phrase, translation, pronunciation}
        for phrase_data in key_phrases_data["phrases"]:
            key_phrases.append({
                "phrase": phrase_data.get("english", ""),
                "translation": phrase_data.get("translation", ""),
                "pronunciation": phrase_data.get("phonetic", "")
            })
    else:
        # Fallback to placeholder phrases if not available
        key_phrases = [
            {"phrase": "Hello", "translation": "Hello (local)", "pronunciation": "he-lo"},
            {"phrase": "Thank you", "translation": "Thank you (local)", "pronunciation": "thank-you"},
            {"phrase": "How much?", "translation": "How much? (local)", "pronunciation": "how-much"},
            {"phrase": "Where is...?", "translation": "Where is...? (local)", "pronunciation": "where-is"},
        ]
    
    essentials = {
        "keyPhrases": key_phrases,
        "etiquetteTips": [
            "Research local customs and etiquette before your trip",
            "Dress appropriately for religious or cultural sites",
            "Be respectful of local traditions and practices",
            "Learn a few basic phrases in the local language",
            "Tip according to local customs"
        ],
        "generalAdvice": [
            "Keep copies of important documents in a secure location",
            "Inform your bank of your travel plans to avoid card issues",
            "Download offline maps for navigation without data",
            "Stay aware of your surroundings and keep valuables secure",
            "Purchase travel insurance for peace of mind",
            "Stay hydrated and protect yourself from the sun",
            "Try local cuisine but be mindful of food safety"
        ],
        "visaRequirements": f"Check visa requirements for {destination} based on your nationality",
        "healthRecommendations": [
            "Consult with a travel health clinic before departure",
            "Ensure routine vaccinations are up to date",
            "Pack a basic first aid kit and any prescription medications",
            "Research local healthcare facilities at your destination"
        ],
        "packingList": [
            "Passport and travel documents",
            "Comfortable walking shoes",
            "Weather-appropriate clothing",
            "Universal power adapter",
            "Portable charger",
            "Basic first aid supplies",
            "Reusable water bottle",
            "Day backpack",
            "Sunscreen and sunglasses",
            "Travel-sized toiletries"
        ]
    }
    
    return essentials


def generate_logistics(destination: str, accommodation: Dict, transport: Dict) -> Dict[str, Any]:
    """
    Generate logistics section with transportation and accommodation info.
    
    Args:
        destination: Destination name
        accommodation: Selected accommodation from AI service
        transport: Selected transport from AI service
        
    Returns:
        Logistics object for frontend
    """
    # Extract accommodation location if available
    accommodation_location = accommodation.get("location", "City Center")
    
    logistics = {
        "neighborhoods": [
            {
                "name": accommodation_location,
                "description": f"Central area in {destination} with good access to attractions",
                "why": "Convenient location for exploring the city"
            },
            {
                "name": "City Center",
                "description": "Heart of the city with major attractions and transport links",
                "why": "Best for first-time visitors who want to see main sights"
            }
        ],
        "transportation": {
            "airport": f"Main airport serving {destination}. Check transport options to city center.",
            "publicTransport": [
                "Local metro/subway system for fast city travel",
                "Bus network covering all areas",
                "Taxis and ride-sharing apps available",
                "Consider getting a multi-day transport pass"
            ],
            "tips": [
                "Download local transport apps for real-time information",
                "Keep small change for public transport",
                "Plan your routes in advance to save time",
                "Consider walking to nearby attractions to experience the city"
            ]
        },
        "keyStations": [
            "Central Station - Main transport hub",
            "Airport - International arrivals/departures",
            f"{accommodation_location} - Your accommodation area"
        ]
    }
    
    return logistics


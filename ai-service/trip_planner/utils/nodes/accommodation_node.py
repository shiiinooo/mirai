"""Accommodation Node - Fetches hotel options and uses LLM to select top 10."""

from typing import Dict, Any
import json
from langchain_core.messages import SystemMessage, HumanMessage

from tracing import observe
from ..state import TripPlannerState
from ..tools import search_hotels
from ..llm_utils import get_llm_for_filtering
from ..json_parser import safe_parse_llm_json_response


@observe(name="accommodation_node")
def accommodation_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Accommodation Node - Fetches hotel options and uses LLM to select top 10
    based on comfort level, budget, and location preferences.
    """
    print("\n🏨 Accommodation Node: Searching for hotels...")
    
    # Fetch all hotels from API
    all_hotels = search_hotels(
        destination=state["destination"],
        travel_dates=state.get("travel_dates"),
        duration=state.get("duration"),
        constraints=state.get("constraints")
    )
    
    print(f"   Found {len(all_hotels)} accommodation options")
    
    # If we have hotels, use LLM to select top 10
    if len(all_hotels) > 0:
        print("   Using LLM to select top 10 accommodations based on preferences...")
        
        # Sort hotels by rating (used for both LLM input and fallback)
        sorted_all = sorted(
            all_hotels,
            key=lambda x: x.get("rating", 0),
            reverse=True
        )
        
        # Initialize LLM (Mistral with OpenAI fallback)
        llm = get_llm_for_filtering(temperature=0.3)
        
        # Get user constraints
        constraints = state.get("constraints", {})
        comfort_level = constraints.get("comfort_level", "standard")
        destination = state["destination"]
        duration = state.get("duration", 3)
        budget = state.get("budget", 0)
        
        # Build system prompt
        system_prompt = """You are a hotel accommodation curator AI. Your job is to select the top 10 hotels 
that best match the user's comfort level and budget constraints.

Consider:
1. Comfort level (backpacker = budget hostels/cheap hotels, standard = mid-range hotels, premium = luxury hotels)
2. Hotel ratings and reviews (prioritize highly-rated hotels)
3. Price per night relative to budget
4. Location (proximity to attractions and city center)
5. Amenities (wifi, breakfast, pool, etc.)
6. Variety of options at different price points

Return your selection as a JSON object with this exact structure:
{
    "selected_hotel_ids": ["hotel_1", "hotel_3", "hotel_5", ...],
    "reasoning": "Brief explanation of why these hotels were selected",
    "selection_criteria": {
        "comfort_level": "standard",
        "price_range": "affordable to mid-range",
        "average_rating": 4.2
    }
}

Select exactly 10 hotels (or fewer if less than 10 are available).
Prioritize hotels with high ratings and good value for money.
"""
        
        # Limit hotels sent to LLM (top 30 by rating to avoid token limits)
        hotels_for_llm = sorted_all[:30]
        
        # Build user prompt with hotel data
        user_prompt = f"""
Destination: {destination}
Trip Duration: {duration} days
Comfort Level: {comfort_level}
Total Budget: ${budget}
Estimated Accommodation Budget: ${budget * 0.3:.0f} (30% of total)

Available Hotels (top {len(hotels_for_llm)} of {len(all_hotels)} total):
{json.dumps(hotels_for_llm, indent=2)}

Select the top 10 hotels that best match the {comfort_level} comfort level and provide best value.
For backpacker level, prioritize budget options. For premium, prioritize luxury and amenities.
"""
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = llm.invoke(messages)
            
            # Parse response using robust JSON parser
            selection = safe_parse_llm_json_response(response.content)
            selected_ids = selection.get("selected_hotel_ids", [])
            
            # Filter hotels based on LLM selection
            selected_hotels = [
                hotel for hotel in all_hotels
                if hotel["id"] in selected_ids
            ]
            
            # If LLM selected fewer than 10, fill with top-rated remaining hotels
            if len(selected_hotels) < 10 and len(selected_hotels) < len(all_hotels):
                remaining_ids = set(selected_ids)
                remaining_hotels = [
                    hotel for hotel in sorted_all
                    if hotel["id"] not in remaining_ids
                ]
                needed = min(10 - len(selected_hotels), len(remaining_hotels))
                selected_hotels.extend(remaining_hotels[:needed])
            
            # Limit to 10
            selected_hotels = selected_hotels[:10]
            
            print(f"   Selected {len(selected_hotels)} top accommodations")
            if "reasoning" in selection:
                print(f"   Reasoning: {selection['reasoning'][:100]}...")
            
            accommodation_options = selected_hotels
            
        except Exception as e:
            print(f"   Warning: LLM selection failed: {e}")
            print("   Falling back to top-rated hotels")
            # Fallback: select top 10 by rating
            accommodation_options = sorted_all[:10]
    else:
        accommodation_options = []
    
    return {
        "accommodation_options": accommodation_options,
        "messages": state.get("messages", []) + [f"Selected {len(accommodation_options)} top accommodations"]
    }


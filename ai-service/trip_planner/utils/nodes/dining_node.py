"""Dining Node - Fetches restaurant options and uses LLM to select top 10."""

from typing import Dict, Any
import json
from langchain_core.messages import SystemMessage, HumanMessage

from tracing import observe
from ..state import TripPlannerState
from ..tools import search_restaurants
from ..llm_utils import get_llm_for_filtering
from ..json_parser import safe_parse_llm_json_response


@observe(name="dining_node")
def dining_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Dining Node - Fetches restaurant options and uses LLM to select top 10
    based on cuisine preferences, budget, and comfort level.
    """
    print("\n🍽️  Dining Node: Searching for restaurants...")
    
    # Fetch all restaurants from API
    all_restaurants = search_restaurants(
        destination=state["destination"],
        preferred_activities=state.get("preferred_activities", []),
        constraints=state.get("constraints")
    )
    
    print(f"   Found {len(all_restaurants)} dining options")
    
    # If we have restaurants, use LLM to select top 10
    if len(all_restaurants) > 0:
        print("   Using LLM to select top 10 restaurants based on preferences...")
        
        # Sort restaurants by rating (used for both LLM input and fallback)
        sorted_all = sorted(
            all_restaurants,
            key=lambda x: x.get("rating", 0),
            reverse=True
        )
        
        # Initialize LLM (Mistral with OpenAI fallback)
        llm = get_llm_for_filtering(temperature=0.3)
        
        # Get user constraints and preferences
        constraints = state.get("constraints", {})
        comfort_level = constraints.get("comfort_level", "standard")
        preferred_activities = state.get("preferred_activities", [])
        destination = state["destination"]
        duration = state.get("duration", 3)
        budget = state.get("budget", 0)
        
        # Extract cuisine preferences
        cuisine_prefs = [act for act in preferred_activities if any(word in act.lower() 
                        for word in ["food", "cuisine", "dining", "restaurant", "local"])]
        
        # Build system prompt
        system_prompt = """You are a restaurant curator AI. Your job is to select the top 10 restaurants 
that best match the user's cuisine preferences, comfort level, and budget.

Consider:
1. Cuisine preferences (if user mentioned specific cuisines or food types)
2. Comfort level (backpacker = cheap eats/street food, standard = mid-range restaurants, premium = fine dining)
3. Restaurant ratings and reviews (prioritize highly-rated places)
4. Price level relative to budget
5. Variety (mix of different cuisines and meal types)
6. Local specialties and must-try restaurants

Return your selection as a JSON object with this exact structure:
{
    "selected_restaurant_ids": ["restaurant_1", "restaurant_3", "restaurant_5", ...],
    "reasoning": "Brief explanation of why these restaurants were selected",
    "selection_criteria": {
        "cuisines": ["Italian", "Local", "Asian"],
        "comfort_level": "standard",
        "price_range": "$$ to $$$"
    }
}

Select exactly 10 restaurants (or fewer if less than 10 are available).
Ensure variety - include breakfast spots, lunch options, and dinner restaurants.
"""
        
        # Limit restaurants sent to LLM (top 30 by rating to avoid token limits)
        restaurants_for_llm = sorted_all[:30]
        
        # Build user prompt with restaurant data
        user_prompt = f"""
Destination: {destination}
Trip Duration: {duration} days
Comfort Level: {comfort_level}
Total Budget: ${budget}
Estimated Dining Budget: ${budget * 0.25:.0f} (25% of total)
Cuisine Preferences: {", ".join(cuisine_prefs) if cuisine_prefs else "Open to all cuisines"}

Available Restaurants (top {len(restaurants_for_llm)} of {len(all_restaurants)} total):
{json.dumps(restaurants_for_llm, indent=2)}

Select the top 10 restaurants that best match the preferences and {comfort_level} comfort level.
Include a variety of meal types (breakfast, lunch, dinner) and cuisines.
For backpacker level, prioritize budget-friendly options. For premium, prioritize fine dining experiences.
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
            selected_ids = selection.get("selected_restaurant_ids", [])
            
            # Filter restaurants based on LLM selection
            selected_restaurants = [
                restaurant for restaurant in all_restaurants
                if restaurant["id"] in selected_ids
            ]
            
            # If LLM selected fewer than 10, fill with top-rated remaining restaurants
            if len(selected_restaurants) < 10 and len(selected_restaurants) < len(all_restaurants):
                remaining_ids = set(selected_ids)
                remaining_restaurants = [
                    restaurant for restaurant in sorted_all
                    if restaurant["id"] not in remaining_ids
                ]
                needed = min(10 - len(selected_restaurants), len(remaining_restaurants))
                selected_restaurants.extend(remaining_restaurants[:needed])
            
            # Limit to 10
            selected_restaurants = selected_restaurants[:10]
            
            print(f"   Selected {len(selected_restaurants)} top restaurants")
            if "reasoning" in selection:
                print(f"   Reasoning: {selection['reasoning'][:100]}...")
            
            dining_options = selected_restaurants
            
        except Exception as e:
            print(f"   Warning: LLM selection failed: {e}")
            print("   Falling back to top-rated restaurants")
            # Fallback: select top 10 by rating
            dining_options = sorted_all[:10]
    else:
        dining_options = []
    
    return {
        "dining_options": dining_options,
        "messages": state.get("messages", []) + [f"Selected {len(dining_options)} top restaurants"]
    }


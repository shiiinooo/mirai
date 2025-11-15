"""Activities Node - Fetches activity/attraction options and uses LLM to select top 10."""

from typing import Dict, Any
from tracing import observe
import json
from langchain_core.messages import SystemMessage, HumanMessage

from ..state import TripPlannerState
from ..tools import search_activities
from ..llm_utils import get_llm_for_filtering
from ..json_parser import safe_parse_llm_json_response


@observe(name="activities_node")
def activities_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Activities Node - Fetches activity/attraction options and uses LLM to select top 10
    based on user preferences and comfort level.
    """
    print("\n🎭 Activities Node: Searching for activities...")
    
    # Fetch all activities from API
    all_activities = search_activities(
        destination=state["destination"],
        preferred_activities=state.get("preferred_activities", []),
        duration=state.get("duration"),
        constraints=state.get("constraints")
    )
    
    print(f"   Found {len(all_activities)} activity options")
    
    # If we have activities, use LLM to select top 10
    if len(all_activities) > 0:
        print("   Using LLM to select top 10 activities based on preferences...")
        
        # Sort activities by rating (used for both LLM input and fallback)
        sorted_all = sorted(
            all_activities,
            key=lambda x: x.get("rating", 0),
            reverse=True
        )
        
        # Initialize LLM (Mistral with OpenAI fallback)
        llm = get_llm_for_filtering(temperature=0.3)
        
        # Get user preferences and constraints
        preferred_activities = state.get("preferred_activities", [])
        constraints = state.get("constraints", {})
        comfort_level = constraints.get("comfort_level", "standard")
        destination = state["destination"]
        duration = state.get("duration", 3)
        
        # Build system prompt
        system_prompt = """You are a travel activities curator AI. Your job is to select the top 10 activities 
that best match the user's preferences and comfort level.

Consider:
1. User's preferred activity types (museums, outdoor, culture, etc.)
2. Comfort level (backpacker = budget-friendly, standard = mid-range, premium = high-end experiences)
3. Destination context and must-see attractions
4. Activity ratings and reviews
5. Variety and balance (mix of different activity types)
6. Duration of the trip (ensure activities fit the trip length)

Return your selection as a JSON object with this exact structure:
{
    "selected_activity_ids": ["activity_1", "activity_3", "activity_5", ...],
    "reasoning": "Brief explanation of why these activities were selected",
    "selection_criteria": {
        "preferences_matched": ["museums", "culture"],
        "comfort_level": "standard",
        "variety": "Mix of indoor and outdoor activities"
    }
}

Select exactly 10 activities (or fewer if less than 10 are available).
Prioritize activities with high ratings and good reviews.
"""
        
        # Limit activities sent to LLM (top 30 by rating to avoid token limits)
        activities_for_llm = sorted_all[:30]  # Send top 30 to LLM
        
        # Build user prompt with activity data
        user_prompt = f"""
Destination: {destination}
Trip Duration: {duration} days
Preferred Activities: {", ".join(preferred_activities) if preferred_activities else "None specified"}
Comfort Level: {comfort_level}

Available Activities (top {len(activities_for_llm)} of {len(all_activities)} total):
{json.dumps(activities_for_llm, indent=2)}

Select the top 10 activities that best match the user's preferences and {comfort_level} comfort level.
Consider the destination context, activity ratings, and ensure variety.
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
            selected_ids = selection.get("selected_activity_ids", [])
            
            # Filter activities based on LLM selection (from all activities, not just the subset)
            selected_activities = [
                activity for activity in all_activities
                if activity["id"] in selected_ids
            ]
            
            # If LLM selected fewer than 10, fill with top-rated remaining activities
            if len(selected_activities) < 10 and len(selected_activities) < len(all_activities):
                remaining_ids = set(selected_ids)
                remaining_activities = [
                    activity for activity in sorted_all  # Use pre-sorted list
                    if activity["id"] not in remaining_ids
                ]
                needed = min(10 - len(selected_activities), len(remaining_activities))
                selected_activities.extend(remaining_activities[:needed])
            
            # Limit to 10
            selected_activities = selected_activities[:10]
            
            print(f"   Selected {len(selected_activities)} top activities")
            if "reasoning" in selection:
                print(f"   Reasoning: {selection['reasoning'][:100]}...")
            
            activities_options = selected_activities
            
        except Exception as e:
            print(f"   Warning: LLM selection failed: {e}")
            print("   Falling back to top-rated activities")
            # Fallback: select top 10 by rating
            activities_options = sorted_all[:10]
    else:
        activities_options = []
    
    return {
        "activities_options": activities_options,
        "messages": state.get("messages", []) + [f"Selected {len(activities_options)} top activities"]
    }


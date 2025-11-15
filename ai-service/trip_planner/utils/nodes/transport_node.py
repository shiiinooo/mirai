"""Transport Node - Fetches flight/transport options and uses LLM to select top 10."""

from typing import Dict, Any
import json
from langchain_core.messages import SystemMessage, HumanMessage

from tracing import observe
from ..state import TripPlannerState
from ..tools import search_flights
from ..llm_utils import get_llm_for_filtering
from ..json_parser import safe_parse_llm_json_response


@observe(name="transport_node")
def transport_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Transport Node - Fetches flight/transport options and uses LLM to select top 10
    based on price, duration, convenience, and comfort level.
    """
    print("\n🚁 Transport Node: Searching for transport options...")
    
    # Fetch all flights from API
    all_flights = search_flights(
        origin=state.get("origin"),
        destination=state["destination"],
        travel_dates=state.get("travel_dates"),
        constraints=state.get("constraints")
    )
    
    print(f"   Found {len(all_flights)} transport options")
    
    # If we have flights, use LLM to select top 10
    if len(all_flights) > 0:
        print("   Using LLM to select top 10 transport options based on preferences...")
        
        # Sort flights by price (used for both LLM input and fallback)
        sorted_all = sorted(
            all_flights,
            key=lambda x: x.get("price", 999999)
        )
        
        # Initialize LLM (Mistral with OpenAI fallback)
        llm = get_llm_for_filtering(temperature=0.3)
        
        # Get user constraints
        constraints = state.get("constraints", {})
        comfort_level = constraints.get("comfort_level", "standard")
        origin = state.get("origin", "Unknown")
        destination = state["destination"]
        budget = state.get("budget", 0)
        
        # Build system prompt
        system_prompt = """You are a flight selection AI. Your job is to select the top 10 flight options 
that best balance price, convenience, and comfort level.

Consider:
1. Price (prioritize good value, but not always the cheapest)
2. Flight duration (shorter is generally better)
3. Number of stops (non-stop preferred, but consider price tradeoff)
4. Departure and arrival times (convenient hours preferred)
5. Comfort level (backpacker = budget flights okay, standard = balance, premium = comfort priority)
6. Airlines (reputable carriers preferred)
7. Variety of options at different price points

Return your selection as a JSON object with this exact structure:
{
    "selected_flight_ids": ["flight_1", "flight_3", "flight_5", ...],
    "reasoning": "Brief explanation of why these flights were selected",
    "selection_criteria": {
        "comfort_level": "standard",
        "price_range": "$300-$800",
        "average_duration": "8h 30m"
    }
}

Select exactly 10 flights (or fewer if less than 10 are available).
Include a mix of budget, mid-range, and premium options if available.
"""
        
        # Limit flights sent to LLM (top 30 by price to avoid token limits)
        flights_for_llm = sorted_all[:30]
        
        # Build user prompt with flight data
        user_prompt = f"""
Origin: {origin}
Destination: {destination}
Comfort Level: {comfort_level}
Total Budget: ${budget}
Estimated Transport Budget: ${budget * 0.35:.0f} (35% of total)

Available Flights (top {len(flights_for_llm)} of {len(all_flights)} total, sorted by price):
{json.dumps(flights_for_llm, indent=2)}

Select the top 10 flights that best match the {comfort_level} comfort level and budget.
For backpacker level, prioritize cheap flights. For premium, prioritize comfort and convenience.
Ensure variety - include both budget and slightly more expensive options for comparison.
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
            selected_ids = selection.get("selected_flight_ids", [])
            
            # Filter flights based on LLM selection
            selected_flights = [
                flight for flight in all_flights
                if flight["id"] in selected_ids
            ]
            
            # If LLM selected fewer than 10, fill with remaining low-price flights
            if len(selected_flights) < 10 and len(selected_flights) < len(all_flights):
                remaining_ids = set(selected_ids)
                remaining_flights = [
                    flight for flight in sorted_all
                    if flight["id"] not in remaining_ids
                ]
                needed = min(10 - len(selected_flights), len(remaining_flights))
                selected_flights.extend(remaining_flights[:needed])
            
            # Limit to 10
            selected_flights = selected_flights[:10]
            
            print(f"   Selected {len(selected_flights)} top transport options")
            if "reasoning" in selection:
                print(f"   Reasoning: {selection['reasoning'][:100]}...")
            
            transport_options = selected_flights
            
        except Exception as e:
            print(f"   Warning: LLM selection failed: {e}")
            print("   Falling back to cheapest flights")
            # Fallback: select top 10 by price
            transport_options = sorted_all[:10]
    else:
        transport_options = []
    
    return {
        "transport_options": transport_options,
        "messages": state.get("messages", []) + [f"Selected {len(transport_options)} top transport options"]
    }


"""Budget Coordinator Node - Uses LLM to select best combination within budget."""

from typing import Dict, Any
import json
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage

from tracing import observe
from ..state import TripPlannerState
from ..tools import estimate_costs
from ..llm_utils import get_llm_for_coordinator
from ..json_parser import safe_parse_llm_json_response


@observe(name="budget_coordinator_node")
def budget_coordinator_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Budget Coordinator Agent - Uses LLM to select best combination within budget.
    Optimizes for value, user preferences, and budget constraints.
    """
    print("\n💰 Budget Coordinator: Analyzing options and selecting best combination...")
    
    # Initialize LLM (Mistral with OpenAI fallback)
    llm = get_llm_for_coordinator(temperature=0.3)
    
    # Get all options
    transport_options = state.get("transport_options", [])
    accommodation_options = state.get("accommodation_options", [])
    activities_options = state.get("activities_options", [])
    dining_options = state.get("dining_options", [])
    
    # Calculate duration
    duration = state.get("duration", 3)
    budget = state["budget"]
    
    # Check if this is an adjustment iteration
    adjustment_iteration = state.get("adjustment_iteration", 0)
    max_iterations = state.get("max_iterations", 2)
    
    # Save state data to JSON file (overwrites on each call)
    state_data = {
        "transport_options": transport_options,
        "accommodation_options": accommodation_options,
        "activities_options": activities_options,
        "dining_options": dining_options,
        "duration": duration,
        "budget": budget,
        "adjustment_iteration": adjustment_iteration,
        "max_iterations": max_iterations,
        "destination": state.get("destination", ""),
        "origin": state.get("origin", ""),
        "preferred_activities": state.get("preferred_activities", []),
        "constraints": state.get("constraints", {})
    }
    
    # Save to JSON file in ai-service directory
    output_file = Path(__file__).parent.parent.parent.parent / "budget_coordinator_state.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        print(f"   [DEBUG] State data saved to {output_file.name}")
    except Exception as e:
        print(f"   [WARNING] Failed to save state data: {e}")
    
    # Build prompt
    system_prompt = """You are a travel budget coordinator AI. Your job is to select the best combination of:
- ONE transport option (from 10 pre-selected best options)
- ONE accommodation option (from 10 pre-selected best options)
- MULTIPLE activities (from 10 pre-selected best options, appropriate for trip duration)
- MULTIPLE restaurants (from 10 pre-selected best options, enough for all meals)

All options have been pre-filtered by specialized AIs based on user preferences and comfort level.
Your job is to create the optimal budget allocation.

You must optimize for:
1. Staying within the total budget (CRITICAL)
2. Maximizing value and quality (all options are already high-quality)
3. Ensuring complete trip coverage (activities and meals for entire duration)
4. Creating a balanced, enjoyable experience

Return your selection as a JSON object with this exact structure:
{
    "selected_transport_id": "flight_X",
    "selected_accommodation_id": "hotel_Y",
    "selected_activity_ids": ["activity_1", "activity_3", "activity_5"],
    "selected_restaurant_ids": ["restaurant_2", "restaurant_4", "restaurant_6"],
    "reasoning": "Brief explanation of your budget allocation strategy",
    "estimated_total": 1500.00,
    "fits_budget": true
}

IMPORTANT: 
- Select enough activities and restaurants for the entire trip duration
- All 10 options in each category are already the best matches for user preferences
- Focus on budget optimization and ensuring comprehensive trip coverage
"""
    
    user_prompt = f"""
Trip Details:
- Destination: {state["destination"]}
- Origin: {state.get("origin", "Unknown")}
- Duration: {duration} days
- Total Budget: ${budget}
- Preferred Activities: {", ".join(state.get("preferred_activities", []))}
- Constraints: {state.get("constraints", {})}
- Adjustment Iteration: {adjustment_iteration} of {max_iterations}

Available Options (all pre-selected by specialized AIs for optimal match):

TRANSPORT OPTIONS (10 best options):
{json.dumps(transport_options, indent=2)}

ACCOMMODATION OPTIONS (10 best options):
{json.dumps(accommodation_options, indent=2)}

ACTIVITIES OPTIONS (10 best options):
{json.dumps(activities_options, indent=2)}

DINING OPTIONS (10 best options):
{json.dumps(dining_options, indent=2)}

Select the best combination that fits within the ${budget} budget.
All options are already optimized for user preferences - focus on budget allocation.
If this is an adjustment iteration ({adjustment_iteration} > 0), prioritize cheaper options.
"""
    
    # Call LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    # Parse response
    try:
        # Use robust JSON parser that handles control characters
        selection = safe_parse_llm_json_response(response.content)
        
        # Get selected items  
        selected_transport_id = selection["selected_transport_id"]
        
        # Find the selected flight (now a single entity that may include round trip)
        selected_transport = next(
            (t for t in transport_options if t["id"] == selected_transport_id),
            transport_options[0] if transport_options else None
        )
        
        # Print raw selected flight data
        if selected_transport:
            print("\n" + "="*80)
            print("RAW SELECTED FLIGHT DATA:")
            print("="*80)
            print(json.dumps(selected_transport, indent=2))
            print("="*80 + "\n")
        
        selected_accommodation = next(
            (h for h in accommodation_options if h["id"] == selection["selected_accommodation_id"]),
            accommodation_options[0] if accommodation_options else None
        )
        
        selected_activities = [
            a for a in activities_options 
            if a["id"] in selection["selected_activity_ids"]
        ]
        
        selected_restaurants = [
            r for r in dining_options 
            if r["id"] in selection["selected_restaurant_ids"]
        ]
        
        # Calculate actual costs
        cost_breakdown = estimate_costs(
            transport=selected_transport,
            accommodation=selected_accommodation,
            activities=selected_activities,
            restaurants=selected_restaurants,
            duration=duration
        )
        
        total_cost = cost_breakdown["total"]
        remaining_budget = budget - total_cost
        fits_budget = total_cost <= budget
        
        # Print transport selection (handle both single flight and round trip)
        if selected_transport:
            if isinstance(selected_transport, list):
                print(f"   Selected transport: {len(selected_transport)} flights (round trip) - ${cost_breakdown['transport']}")
            else:
                print(f"   Selected transport: {selected_transport.get('airline', 'Unknown')} - ${selected_transport.get('price', 0)}")
        else:
            print("   Selected transport: None - $0")
        print(f"   Selected accommodation: {selected_accommodation['name'] if selected_accommodation else 'None'} - ${selected_accommodation['total_price'] if selected_accommodation else 0}")
        print(f"   Selected {len(selected_activities)} activities - ${cost_breakdown['activities']}")
        print(f"   Selected {len(selected_restaurants)} restaurants - ${cost_breakdown['dining']}")
        print(f"   Total cost: ${total_cost:.2f} / ${budget}")
        print(f"   Fits budget: {fits_budget}")
        
        return {
            "selected_transport": selected_transport,
            "selected_accommodation": selected_accommodation,
            "selected_activities": selected_activities,
            "selected_restaurants": selected_restaurants,
            "cost_breakdown": cost_breakdown,
            "total_cost": total_cost,
            "remaining_budget": remaining_budget,
            "requires_adjustment": not fits_budget,
            "adjustment_iteration": adjustment_iteration,
            "messages": state.get("messages", []) + [f"Budget coordination complete: ${total_cost:.2f}"]
        }
        
    except Exception as e:
        print(f"   Error parsing LLM response: {e}")
        # Fallback: select cheapest options
        selected_transport = transport_options[0] if transport_options else None
        selected_accommodation = accommodation_options[0] if accommodation_options else None
        selected_activities = activities_options[:5] if activities_options else []
        selected_restaurants = dining_options[:duration * 2] if dining_options else []
        
        cost_breakdown = estimate_costs(
            transport=selected_transport,
            accommodation=selected_accommodation,
            activities=selected_activities,
            restaurants=selected_restaurants,
            duration=duration
        )
        
        total_cost = cost_breakdown["total"]
        
        return {
            "selected_transport": selected_transport,
            "selected_accommodation": selected_accommodation,
            "selected_activities": selected_activities,
            "selected_restaurants": selected_restaurants,
            "cost_breakdown": cost_breakdown,
            "total_cost": total_cost,
            "remaining_budget": budget - total_cost,
            "requires_adjustment": total_cost > budget,
            "adjustment_iteration": adjustment_iteration,
            "messages": state.get("messages", []) + ["Budget coordination complete (fallback)"]
        }


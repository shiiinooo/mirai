"""Itinerary Generator Node - Uses LLM to create coherent day-by-day schedule."""

from typing import Dict, Any
import json
from langchain_core.messages import SystemMessage, HumanMessage

from tracing import observe
from ..state import TripPlannerState
from ..llm_utils import get_llm
from ..json_parser import safe_parse_llm_json_response


@observe(name="itinerary_generator_node")
def itinerary_generator_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Itinerary Generator Agent - Uses LLM to create coherent day-by-day schedule.
    Orders activities logically and adds context/explanations.
    """
    print("\n📋 Itinerary Generator: Creating day-by-day schedule...")
    
    # Initialize LLM
    # Initialize LLM (Mistral with OpenAI fallback) - higher temperature for creativity
    llm = get_llm(temperature=0.7)
    
    duration = state.get("duration", 3)
    
    # Build prompt
    system_prompt = """You are a travel itinerary generator AI. Create a detailed, well-structured day-by-day itinerary.

CRITICAL: You MUST return a JSON object with this EXACT structure. Every day must have at least one activity or restaurant.

Consider:
- Logical ordering (morning to evening)
- Geographic proximity (minimize travel between locations)
- Meal times (breakfast around 8-9am, lunch around 12-1pm, dinner around 7-8pm)
- Activity timing and duration
- Rest periods and reasonable pacing
- Use the EXACT activity and restaurant names from the provided lists

Return a JSON object with this EXACT structure (no variations):
{
    "itinerary": [
        {
            "day": 1,
            "morning": {
                "time": "9:00 AM",
                "activity": "EXACT activity name from the ACTIVITIES list",
                "description": "Brief description of what to do",
                "estimated_cost": 25.00
            },
            "lunch": {
                "time": "12:30 PM",
                "restaurant": "EXACT restaurant name from the RESTAURANTS list",
                "cuisine": "Italian",
                "estimated_cost": 30.00
            },
            "afternoon": {
                "time": "2:00 PM",
                "activity": "EXACT activity name from the ACTIVITIES list",
                "description": "Brief description",
                "estimated_cost": 20.00
            },
            "dinner": {
                "time": "7:00 PM",
                "restaurant": "EXACT restaurant name from the RESTAURANTS list",
                "cuisine": "Local",
                "estimated_cost": 35.00
            },
            "evening": {
                "time": "8:30 PM",
                "activity": "EXACT activity name from the ACTIVITIES list (REQUIRED)",
                "description": "Brief description",
                "estimated_cost": 15.00
            }
        }
    ]
}

IMPORTANT RULES:
1. Use EXACT names from the ACTIVITIES and RESTAURANTS lists provided
2. Every day MUST have morning, lunch, afternoon, dinner, AND evening slots filled
3. Evening slot is MANDATORY - include an activity or restaurant for every evening
4. Distribute activities and restaurants evenly across all days
5. Each slot must be a dictionary with "time", "activity" OR "restaurant", "description", and "estimated_cost"
6. Do NOT create new activity or restaurant names - only use names from the provided lists
"""
    
    user_prompt = f"""
Trip Details:
- Destination: {state["destination"]}
- Duration: {duration} days
- Budget: ${state["budget"]}
- Remaining Budget: ${state.get("remaining_budget", 0):.2f}

Selected Options:

TRANSPORT:
{json.dumps(state.get("selected_transport"), indent=2)}

ACCOMMODATION:
{json.dumps(state.get("selected_accommodation"), indent=2)}

ACTIVITIES:
{json.dumps(state.get("selected_activities", []), indent=2)}

RESTAURANTS:
{json.dumps(state.get("selected_restaurants", []), indent=2)}

COST BREAKDOWN:
{json.dumps(state.get("cost_breakdown"), indent=2)}

Create a detailed {duration}-day itinerary that incorporates all selected activities and restaurants.
Arrange them in a logical, enjoyable sequence.
"""
    
    # Call LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    # Parse response using robust JSON parser
    try:
        itinerary = safe_parse_llm_json_response(response.content)
        
        print(f"   ✅ Generated {duration}-day itinerary")
        print(f"   Total activities: {len(state.get('selected_activities', []))}")
        print(f"   Total restaurants: {len(state.get('selected_restaurants', []))}")
        
        # Validate and ensure itinerary has proper structure
        itinerary_list = itinerary.get("itinerary", [])
        
        # If itinerary is empty or invalid, use fallback
        if not itinerary_list or len(itinerary_list) == 0:
            print(f"   Warning: LLM returned empty itinerary, using fallback")
            raise ValueError("Empty itinerary from LLM")
        
        # Validate each day has required structure
        validated_itinerary = []
        for day_plan in itinerary_list:
            if not isinstance(day_plan, dict):
                continue
            if "day" not in day_plan:
                continue
            # Ensure required slots exist (morning, lunch, afternoon, dinner, evening)
            required_slots = ["morning", "lunch", "afternoon", "dinner", "evening"]
            has_all_slots = all(
                slot in day_plan and isinstance(day_plan[slot], dict) and 
                ("activity" in day_plan[slot] or "restaurant" in day_plan[slot])
                for slot in required_slots
            )
            if has_all_slots:
                validated_itinerary.append(day_plan)
            else:
                # Log which slots are missing for debugging
                missing_slots = [slot for slot in required_slots 
                               if slot not in day_plan or not isinstance(day_plan[slot], dict) or 
                               ("activity" not in day_plan[slot] and "restaurant" not in day_plan[slot])]
                print(f"   Warning: Day {day_plan.get('day', '?')} missing slots: {missing_slots}")
        
        if len(validated_itinerary) == 0:
            print(f"   Warning: No valid days in itinerary, using fallback")
            raise ValueError("No valid days in itinerary")
        
        print(f"   ✅ Validated {len(validated_itinerary)} days in itinerary")
        
        # Build final output
        final_output = {
            "itinerary": validated_itinerary,
            "transport": state.get("selected_transport"),
            "accommodation": state.get("selected_accommodation"),
            "selected_activities": state.get("selected_activities", []),
            "selected_restaurants": state.get("selected_restaurants", []),
            "cost_breakdown": state.get("cost_breakdown"),
            "total_cost": state.get("total_cost"),
            "remaining_budget": state.get("remaining_budget"),
            "summary": itinerary.get("summary", {}),
            "tips": itinerary.get("tips", []),
            "key_phrases": state.get("key_phrases"),
            "activity_stories": state.get("activity_stories", {})
        }
        
        return {
            "final_itinerary": final_output,
            "messages": state.get("messages", []) + ["Itinerary generation complete"]
        }
        
    except Exception as e:
        print(f"   Error parsing itinerary: {e}")
        print(f"   Creating fallback itinerary from selected activities and restaurants")
        
        # Create a proper fallback itinerary using selected activities and restaurants
        selected_activities = state.get("selected_activities", [])
        selected_restaurants = state.get("selected_restaurants", [])
        
        fallback_itinerary = []
        activity_idx = 0
        restaurant_idx = 0
        
        for day_num in range(1, duration + 1):
            day_plan = {"day": day_num}
            
            # Morning activity
            if activity_idx < len(selected_activities):
                activity = selected_activities[activity_idx]
                day_plan["morning"] = {
                    "time": "9:00 AM",
                    "activity": activity.get("name", "Activity"),
                    "description": activity.get("description", activity.get("snippet", "Explore and enjoy")),
                    "estimated_cost": activity.get("price", activity.get("cost", 0))
                }
                activity_idx += 1
            
            # Lunch restaurant
            if restaurant_idx < len(selected_restaurants):
                restaurant = selected_restaurants[restaurant_idx]
                day_plan["lunch"] = {
                    "time": "12:30 PM",
                    "restaurant": restaurant.get("name", "Restaurant"),
                    "cuisine": restaurant.get("cuisine", "Local"),
                    "estimated_cost": restaurant.get("avg_cost_per_person", restaurant.get("price", 0))
                }
                restaurant_idx += 1
            
            # Afternoon activity
            if activity_idx < len(selected_activities):
                activity = selected_activities[activity_idx]
                day_plan["afternoon"] = {
                    "time": "2:00 PM",
                    "activity": activity.get("name", "Activity"),
                    "description": activity.get("description", activity.get("snippet", "Explore and enjoy")),
                    "estimated_cost": activity.get("price", activity.get("cost", 0))
                }
                activity_idx += 1
            
            # Dinner restaurant
            if restaurant_idx < len(selected_restaurants):
                restaurant = selected_restaurants[restaurant_idx]
                day_plan["dinner"] = {
                    "time": "7:00 PM",
                    "restaurant": restaurant.get("name", "Restaurant"),
                    "cuisine": restaurant.get("cuisine", "Local"),
                    "estimated_cost": restaurant.get("avg_cost_per_person", restaurant.get("price", 0))
                }
                restaurant_idx += 1
            
            # Evening activity (REQUIRED - use restaurant if no more activities)
            if activity_idx < len(selected_activities):
                activity = selected_activities[activity_idx]
                day_plan["evening"] = {
                    "time": "8:00 PM",
                    "activity": activity.get("name", "Activity"),
                    "description": activity.get("description", activity.get("snippet", "Explore and enjoy")),
                    "estimated_cost": activity.get("price", activity.get("cost", 0))
                }
                activity_idx += 1
            elif restaurant_idx < len(selected_restaurants):
                # Use a restaurant for evening if no more activities
                restaurant = selected_restaurants[restaurant_idx]
                day_plan["evening"] = {
                    "time": "8:00 PM",
                    "restaurant": restaurant.get("name", "Restaurant"),
                    "cuisine": restaurant.get("cuisine", "Local"),
                    "estimated_cost": restaurant.get("avg_cost_per_person", restaurant.get("price", 0))
                }
                restaurant_idx += 1
            else:
                # Fallback: create a placeholder evening activity
                day_plan["evening"] = {
                    "time": "8:00 PM",
                    "activity": "Evening exploration",
                    "description": "Explore the local area and enjoy the evening atmosphere",
                    "estimated_cost": 0
                }
            
            fallback_itinerary.append(day_plan)
        
        final_output = {
            "itinerary": fallback_itinerary,
            "transport": state.get("selected_transport"),
            "accommodation": state.get("selected_accommodation"),
            "selected_activities": selected_activities,
            "selected_restaurants": selected_restaurants,
            "cost_breakdown": state.get("cost_breakdown"),
            "total_cost": state.get("total_cost"),
            "remaining_budget": state.get("remaining_budget"),
            "key_phrases": state.get("key_phrases")
        }
        
        return {
            "final_itinerary": final_output,
            "messages": state.get("messages", []) + ["Itinerary generation complete (fallback)"]
        }


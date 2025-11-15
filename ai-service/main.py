"""
Main entry point for the Trip Planner Multi-Agent System.

Usage:
    python main.py
"""

import os
import json
from dotenv import load_dotenv
from trip_planner.agent import get_compiled_graph


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_section_header(title):
    """Print a formatted section header."""
    print_separator()
    print(f"  {title}")
    print_separator()


def format_itinerary_output(result):
    """Format and print the final itinerary in a readable way."""
    
    if "final_itinerary" not in result:
        print("⚠️  No itinerary generated.")
        return
    
    itinerary_data = result["final_itinerary"]
    
    # Print Transport
    print_section_header("🚁 TRANSPORT")
    transport = itinerary_data.get("transport", {})
    if transport:
        print(f"Airline: {transport.get('airline', 'N/A')}")
        print(f"Flight: {transport.get('flight_number', 'N/A')}")
        print(f"Route: {transport.get('origin', 'N/A')} → {transport.get('destination', 'N/A')}")
        print(f"Departure: {transport.get('departure_time', 'N/A')}")
        print(f"Arrival: {transport.get('arrival_time', 'N/A')}")
        print(f"Class: {transport.get('class', 'N/A')}")
        print(f"Price: ${transport.get('price', 0):.2f}")
    
    # Print Accommodation
    print_section_header("🏨 ACCOMMODATION")
    accommodation = itinerary_data.get("accommodation", {})
    if accommodation:
        print(f"Name: {accommodation.get('name', 'N/A')}")
        print(f"Type: {accommodation.get('type', 'N/A')}")
        print(f"Rating: {accommodation.get('rating', 0)}⭐ ({accommodation.get('reviews', 0)} reviews)")
        print(f"Location: {accommodation.get('location', 'N/A')}")
        print(f"Price per night: ${accommodation.get('price_per_night', 0):.2f}")
        print(f"Total price: ${accommodation.get('total_price', 0):.2f}")
        print(f"Amenities: {', '.join(accommodation.get('amenities', []))}")
    
    # Print Itinerary
    print_section_header("📋 DAILY ITINERARY")
    itinerary = itinerary_data.get("itinerary", [])
    
    if isinstance(itinerary, list) and len(itinerary) > 0:
        for day_plan in itinerary:
            day = day_plan.get("day", "?")
            date = day_plan.get("date", "")
            print(f"\n━━━ Day {day} {f'({date})' if date else ''} ━━━")
            
            # Print each time slot
            for slot in ["morning", "lunch", "afternoon", "dinner", "evening"]:
                if slot in day_plan:
                    slot_data = day_plan[slot]
                    time = slot_data.get("time", "")
                    
                    if "activity" in slot_data:
                        print(f"\n  {time} - {slot_data.get('activity', 'Activity')}")
                        if "description" in slot_data:
                            print(f"    {slot_data['description']}")
                        if "estimated_cost" in slot_data:
                            print(f"    Cost: ${slot_data['estimated_cost']:.2f}")
                    
                    elif "restaurant" in slot_data:
                        print(f"\n  {time} - 🍽️  {slot_data.get('restaurant', 'Restaurant')}")
                        if "cuisine" in slot_data:
                            print(f"    Cuisine: {slot_data['cuisine']}")
                        if "estimated_cost" in slot_data:
                            print(f"    Cost: ${slot_data['estimated_cost']:.2f}")
    else:
        print("\n⚠️  Detailed day-by-day itinerary not available.")
        print("\nSelected Activities:")
        for activity in itinerary_data.get("selected_activities", [])[:10]:
            print(f"  • {activity.get('name', 'Activity')} - ${activity.get('price', 0)}")
        
        print("\nSelected Restaurants:")
        for restaurant in itinerary_data.get("selected_restaurants", [])[:8]:
            print(f"  • {restaurant.get('name', 'Restaurant')} - {restaurant.get('cuisine', 'Various')}")
    
    # Print Cost Breakdown
    print_section_header("💰 COST BREAKDOWN")
    cost_breakdown = itinerary_data.get("cost_breakdown", {})
    
    print(f"Transport:        ${cost_breakdown.get('transport', 0):>10.2f}")
    print(f"Accommodation:    ${cost_breakdown.get('accommodation', 0):>10.2f}")
    print(f"Activities:       ${cost_breakdown.get('activities', 0):>10.2f}")
    print(f"Dining:           ${cost_breakdown.get('dining', 0):>10.2f}")
    print(f"Miscellaneous:    ${cost_breakdown.get('miscellaneous', 0):>10.2f}")
    print("-" * 40)
    print(f"TOTAL:            ${cost_breakdown.get('total', 0):>10.2f}")
    print(f"Remaining Budget: ${itinerary_data.get('remaining_budget', 0):>10.2f}")
    
    # Print Key Phrases
    key_phrases_data = itinerary_data.get("key_phrases")
    if key_phrases_data:
        print_section_header("🗣️  KEY PHRASES")
        language = key_phrases_data.get("language", "Unknown")
        phrases = key_phrases_data.get("phrases", [])
        
        if phrases:
            print(f"Language: {language}\n")
            for phrase in phrases:
                english = phrase.get("english", "")
                translation = phrase.get("translation", "")
                phonetic = phrase.get("phonetic", "")
                
                print(f"  {english}")
                print(f"    {translation}")
                if phonetic:
                    print(f"    ({phonetic})")
                print()
        else:
            print("No phrases available.")
    
    # Print Tips
    if "tips" in itinerary_data and itinerary_data["tips"]:
        print_section_header("💡 TRAVEL TIPS")
        for i, tip in enumerate(itinerary_data["tips"], 1):
            print(f"{i}. {tip}")
    
    print_separator()


def run_trip_planner(user_input):
    """
    Run the trip planner workflow with user input.
    
    Args:
        user_input: Dictionary containing trip requirements
    """
    print("\n" + "="*80)
    print("🌍  TRIP PLANNER MULTI-AGENT SYSTEM")
    print("="*80)
    
    print("\n📝 Trip Requirements:")
    print(f"   Destination: {user_input.get('destination', 'N/A')}")
    print(f"   Origin: {user_input.get('origin', 'N/A')}")
    print(f"   Duration: {user_input.get('duration', 'N/A')} days")
    print(f"   Budget: ${user_input.get('budget', 0)}")
    print(f"   Interests: {', '.join(user_input.get('preferred_activities', []))}")
    
    print("\n🚀 Starting workflow...\n")
    
    # Initialize the state with user input
    initial_state = {
        "destination": user_input["destination"],
        "origin": user_input.get("origin"),
        "travel_dates": user_input.get("travel_dates"),
        "duration": user_input.get("duration", 3),
        "budget": user_input["budget"],
        "preferred_activities": user_input.get("preferred_activities", []),
        "constraints": user_input.get("constraints", {}),
        # Initialize empty lists/values
        "transport_options": [],
        "accommodation_options": [],
        "activities_options": [],
        "dining_options": [],
        "key_phrases": None,
        "selected_transport": None,
        "selected_accommodation": None,
        "selected_activities": [],
        "selected_restaurants": [],
        "total_cost": 0.0,
        "remaining_budget": user_input["budget"],
        "cost_breakdown": {},
        "requires_adjustment": False,
        "adjustment_iteration": 0,
        "max_iterations": 2,
        "final_itinerary": None,
        "messages": []
    }
    
    # Get the compiled graph
    graph = get_compiled_graph()
    
    # Run the workflow
    try:
        result = graph.invoke(initial_state)
        
        print("\n✅ Workflow completed successfully!\n")
        
        # Format and print the output
        format_itinerary_output(result)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error running workflow: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function with example trip request."""
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in your .env file or environment.")
        return
    
    example_trip = {
        "destination": "Tokyo, Japan",
        "origin": "New York, USA Paris, France",
        "travel_dates": {
            "start": "2025-11-15",
            "end": "2025-11-20"
        },
        "duration": 5,
        "budget": 5000,
        "preferred_activities": [
            "museums",
            "food",
            "culture",
            "nightlife"
        ],
        "constraints": {
            "comfort_level": "mid",
            "allergies": [],
            "walking_distance": 5  # km per day
        }
    }
    
    # Run the trip planner with Example 1
    print("\n" + "🌟"*40)
    print("Running Example Trip: Japan Trip")
    print("🌟"*40 + "\n")
    
    result = run_trip_planner(example_trip)
    
    # Optionally save the result to a file
    if result and result.get("final_itinerary"):
        output_file = "trip_itinerary.json"
        with open(output_file, "w") as f:
            json.dump(result["final_itinerary"], f, indent=2)
        print(f"\n💾 Full itinerary saved to: {output_file}")
    
    print("\n" + "="*80)
    print("✨ Trip planning complete! Have a wonderful journey! ✨")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()


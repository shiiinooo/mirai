"""
Test script to validate the trip planner structure without requiring API keys.
This tests imports, state initialization, and graph construction.
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from trip_planner.utils.state import TripPlannerState
        print("✅ State module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import state: {e}")
        return False
    
    try:
        from trip_planner.utils.tools import (
            search_flights,
            search_hotels,
            search_activities,
            search_restaurants,
            estimate_costs
        )
        print("✅ Tools module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import tools: {e}")
        return False
    
    try:
        from trip_planner.utils.nodes import (
            transport_node,
            accommodation_node,
            activities_node,
            dining_node,
            budget_coordinator_node,
            itinerary_generator_node
        )
        print("✅ Nodes module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import nodes: {e}")
        return False
    
    try:
        from trip_planner.agent import create_trip_planner_graph, get_compiled_graph
        print("✅ Agent module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import agent: {e}")
        return False
    
    return True


def test_mock_tools():
    """Test that mock data tools work correctly."""
    print("\nTesting mock data tools...")
    
    from trip_planner.utils.tools import (
        search_flights,
        search_hotels,
        search_activities,
        search_restaurants
    )
    
    try:
        # Test flights
        flights = search_flights(
            origin="New York",
            destination="Paris",
            travel_dates={"start": "2024-06-15", "end": "2024-06-20"},
            constraints={"comfort_level": "mid"}
        )
        assert len(flights) >= 5, "Should return at least 5 flights"
        assert all("price" in f for f in flights), "All flights should have price"
        print(f"✅ search_flights returned {len(flights)} options")
        
        # Test hotels
        hotels = search_hotels(
            destination="Paris",
            travel_dates={"start": "2024-06-15", "end": "2024-06-20"},
            duration=5,
            constraints={"comfort_level": "mid"}
        )
        assert len(hotels) >= 10, "Should return at least 10 hotels"
        assert all("price_per_night" in h for h in hotels), "All hotels should have price"
        print(f"✅ search_hotels returned {len(hotels)} options")
        
        # Test activities
        activities = search_activities(
            destination="Paris",
            preferred_activities=["museums", "food"],
            duration=5,
            constraints={}
        )
        assert len(activities) >= 15, "Should return at least 15 activities"
        assert all("price" in a for a in activities), "All activities should have price"
        print(f"✅ search_activities returned {len(activities)} options")
        
        # Test restaurants
        restaurants = search_restaurants(
            destination="Paris",
            preferred_activities=["food"],
            constraints={}
        )
        assert len(restaurants) >= 15, "Should return at least 15 restaurants"
        assert all("avg_cost_per_person" in r for r in restaurants), "All restaurants should have cost"
        print(f"✅ search_restaurants returned {len(restaurants)} options")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_construction():
    """Test that the graph can be constructed."""
    print("\nTesting graph construction...")
    
    try:
        from trip_planner.agent import create_trip_planner_graph
        
        workflow = create_trip_planner_graph()
        print("✅ Graph created successfully")
        
        # Try to compile it
        graph = workflow.compile()
        print("✅ Graph compiled successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Graph construction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_fetching_nodes():
    """Test data-fetching nodes without LLM."""
    print("\nTesting data-fetching nodes...")
    
    from trip_planner.utils.nodes import (
        transport_node,
        accommodation_node,
        activities_node,
        dining_node
    )
    
    # Create test state
    test_state = {
        "destination": "Paris, France",
        "origin": "New York, USA",
        "duration": 5,
        "budget": 3000,
        "preferred_activities": ["museums", "food"],
        "constraints": {"comfort_level": "mid"},
        "messages": []
    }
    
    try:
        # Test transport node
        result = transport_node(test_state)
        assert "transport_options" in result, "Should return transport_options"
        assert len(result["transport_options"]) > 0, "Should have transport options"
        print(f"✅ transport_node returned {len(result['transport_options'])} options")
        
        # Test accommodation node
        result = accommodation_node(test_state)
        assert "accommodation_options" in result, "Should return accommodation_options"
        assert len(result["accommodation_options"]) > 0, "Should have accommodation options"
        print(f"✅ accommodation_node returned {len(result['accommodation_options'])} options")
        
        # Test activities node
        result = activities_node(test_state)
        assert "activities_options" in result, "Should return activities_options"
        assert len(result["activities_options"]) > 0, "Should have activity options"
        print(f"✅ activities_node returned {len(result['activities_options'])} options")
        
        # Test dining node
        result = dining_node(test_state)
        assert "dining_options" in result, "Should return dining_options"
        assert len(result["dining_options"]) > 0, "Should have dining options"
        print(f"✅ dining_node returned {len(result['dining_options'])} options")
        
        return True
        
    except Exception as e:
        print(f"❌ Data-fetching nodes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("  TRIP PLANNER STRUCTURE VALIDATION TEST")
    print("="*80)
    
    tests = [
        ("Module Imports", test_imports),
        ("Mock Data Tools", test_mock_tools),
        ("Graph Construction", test_graph_construction),
        ("Data-Fetching Nodes", test_data_fetching_nodes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe trip planner structure is valid and ready to use.")
        print("\nTo run the full workflow:")
        print("1. Add your OpenAI API key to .env file")
        print("2. Run: python main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease check the errors above and fix them.")
    print("="*80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


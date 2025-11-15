"""LangGraph workflow construction for the trip planner."""

from typing import Literal
from langgraph.graph import StateGraph, START, END  # ✅ import START

from .utils.state import TripPlannerState
from .utils.nodes import (
    transport_node,
    accommodation_node,
    activities_node,
    dining_node,
    key_phrases_node,
    budget_coordinator_node,
    itinerary_generator_node,
    story_generator_node,
)


def should_adjust_budget(state: TripPlannerState) -> Literal["adjust", "generate"]:
    """
    Conditional routing function to decide if budget adjustment is needed.
    
    Returns:
        "adjust": If budget exceeded and haven't hit max iterations
        "generate": If budget OK or max iterations reached
    """
    requires_adjustment = state.get("requires_adjustment", False)
    adjustment_iteration = state.get("adjustment_iteration", 0)
    max_iterations = state.get("max_iterations", 2)
    
    if requires_adjustment and adjustment_iteration < max_iterations:
        print(f"\n⚠️  Budget exceeded. Attempting adjustment {adjustment_iteration + 1}/{max_iterations}...")
        # Increment adjustment iteration
        state["adjustment_iteration"] = adjustment_iteration + 1
        return "adjust"
    else:
        if requires_adjustment:
            print(f"\n⚠️  Budget still exceeded after {max_iterations} adjustments. Proceeding with best effort...")
        else:
            print("\n✅ Budget OK. Proceeding to itinerary generation...")
        return "generate"


def create_trip_planner_graph() -> StateGraph:
    """
    Create and return the trip planner workflow graph.
    
    Graph Structure:
    1. START → [transport, accommodation, activities, dining, key_phrases] (parallel)
    2. activities → story_generator
    3. [transport, accommodation, dining, key_phrases, story_generator] → budget_coordinator (deferred)
    4. budget_coordinator → conditional routing:
       - "adjust"   → budget_coordinator (retry with stricter filtering)
       - "generate" → itinerary_generator
    5. itinerary_generator → END
    """
    
    # Initialize the graph with our state schema
    workflow = StateGraph(TripPlannerState)
    
    # Add all nodes
    workflow.add_node("transport", transport_node)
    workflow.add_node("accommodation", accommodation_node)
    workflow.add_node("activities", activities_node)
    workflow.add_node("story_generator", story_generator_node)
    workflow.add_node("dining", dining_node)
    workflow.add_node("key_phrases", key_phrases_node)
    
    # ✅ Make budget_coordinator deferred so it waits for all non-deferred work
    workflow.add_node("budget_coordinator", budget_coordinator_node, defer=True)
    workflow.add_node("itinerary_generator", itinerary_generator_node)
    
    # ✅ Phase 1: START fans out to all research nodes in parallel
    workflow.add_edge(START, "transport")
    workflow.add_edge(START, "accommodation")
    workflow.add_edge(START, "activities")
    workflow.add_edge(START, "dining")
    workflow.add_edge(START, "key_phrases")
    
    # Activities → Story generator
    workflow.add_edge("activities", "story_generator")
    
    # All branches converge into budget_coordinator
    workflow.add_edge("transport", "budget_coordinator")
    workflow.add_edge("accommodation", "budget_coordinator")
    workflow.add_edge("dining", "budget_coordinator")
    workflow.add_edge("key_phrases", "budget_coordinator")
    workflow.add_edge("story_generator", "budget_coordinator")
    
    # Phase 2: Budget coordinator with conditional routing
    workflow.add_conditional_edges(
        "budget_coordinator",
        should_adjust_budget,
        {
            "adjust": "budget_coordinator",      # Loop back to retry
            "generate": "itinerary_generator",   # Proceed to final generation
        },
    )
    
    # Phase 3: Itinerary generator completes the workflow
    workflow.add_edge("itinerary_generator", END)
    
    return workflow


# Compile the graph for use
def get_compiled_graph():
    """Get the compiled graph ready for execution."""
    workflow = create_trip_planner_graph()
    return workflow.compile()


# Export the compiled graph
graph = get_compiled_graph()

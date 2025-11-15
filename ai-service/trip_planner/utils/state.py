"""State definition for the trip planner graph."""

from typing import TypedDict, List, Optional, Dict, Any, Annotated
from datetime import date
import operator


class TripPlannerState(TypedDict):
    """
    State schema for the trip planner multi-agent workflow.
    
    This state is shared across all agents in the graph.
    """
    
    # User Inputs
    destination: str
    origin: Optional[str]
    travel_dates: Optional[Dict[str, str]]  # {"start": "2024-06-15", "end": "2024-06-20"}
    duration: Optional[int]  # Duration in days
    budget: float
    preferred_activities: List[str]  # ["museums", "nightlife", "hiking", "food"]
    constraints: Optional[Dict[str, Any]]  # {"comfort_level": "mid", "allergies": [...], "walking_distance": 5}
    
    # Data Fetching Results (from parallel agents)
    transport_options: List[Dict[str, Any]]  # List of flight/transport options
    accommodation_options: List[Dict[str, Any]]  # List of hotel options
    activities_options: List[Dict[str, Any]]  # List of activity/attraction options
    dining_options: List[Dict[str, Any]]  # List of restaurant options
    key_phrases: Optional[Dict[str, Any]]  # Key phrases for destination language
    activity_stories: Dict[str, str]  # Mapping of activity_id to story text
    
    # Budget Coordinator Selections
    selected_transport: Optional[Dict[str, Any]]
    selected_accommodation: Optional[Dict[str, Any]]
    selected_activities: List[Dict[str, Any]]
    selected_restaurants: List[Dict[str, Any]]
    
    # Budget Tracking
    total_cost: float
    remaining_budget: float
    cost_breakdown: Dict[str, float]  # {"transport": 450, "accommodation": 600, ...}
    
    # Workflow Control
    requires_adjustment: bool
    adjustment_iteration: int
    max_iterations: int
    
    # Final Output
    final_itinerary: Optional[Dict[str, Any]]
    
    # Messages (for LangGraph message passing)
    # Use Annotated with operator.add to merge messages from parallel nodes
    messages: Annotated[List[str], operator.add]


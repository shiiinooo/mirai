"""Story Generator Node - Generates short stories for activities."""

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from tracing import observe
from ..state import TripPlannerState
from ..llm_utils import get_llm
from ..db import get_story_by_place, store_place_story


@observe(name="story_generator_node")
def story_generator_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Story Generator Node - Generates very short stories (2-3 sentences) for each activity.
    
    Checks Qdrant DB first for existing stories, then generates new ones if needed.
    Saves all new stories to Qdrant for future use.
    Creates engaging, contextual stories that will be ~30 seconds when spoken.
    """
    print("\n📖 Story Generator: Creating stories for activities...")
    
    activities_options = state.get("activities_options", [])
    destination = state.get("destination", "")
    
    if not activities_options:
        print("   No activities to generate stories for")
        return {
            "activity_stories": {},
            "messages": state.get("messages", []) + ["No activities to generate stories for"]
        }
    
    # Initialize LLM (Mistral with OpenAI fallback)
    llm = get_llm(temperature=0.7)
    
    activity_stories = {}
    stories_from_db = 0
    stories_generated = 0
    stories_saved = 0
    
    # Process each activity
    for activity in activities_options:
        activity_id = activity.get("id", "")
        activity_name = activity.get("name", "Activity")
        activity_description = activity.get("description", "")
        activity_type = activity.get("type", "")
        
        if not activity_id:
            continue
        
        # Prepare location for Qdrant lookup (format: "City, Country" or just "City")
        location = destination  # Use destination as location
        
        # Step 1: Check Qdrant DB for existing story
        existing_story = None
        try:
            existing_story_data = get_story_by_place(
                place_name=activity_name,
                location=location
            )
            if existing_story_data and existing_story_data.get("story"):
                existing_story = existing_story_data.get("story")
                activity_stories[activity_id] = existing_story
                stories_from_db += 1
                print(f"   ✅ Found existing story in DB for: {activity_name}")
                continue
        except Exception as e:
            print(f"   ⚠️  Error checking Qdrant for {activity_name}: {e}")
            # Continue to generate new story if DB check fails
        
        # Step 2: Generate new story if not found in DB
        system_prompt = """Write a short 2–3 sentence guide-style narrative about this place or activity:

If the place has historical or cultural significance, include a brief fact or background.
If it's a modern activity with no history, share an interesting fact or insight about the area instead. 
Make it immersive and easy for the traveler to picture.
Return only the story text, no additional commentary."""
        
        user_prompt = f"""Write a very short story (2-3 sentences) about visiting this activity:

Activity: {activity_name}
Type: {activity_type}
Description: {activity_description}
Destination: {destination}

Make it engaging and help the traveler imagine the experience."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            story = response.content.strip()
            
            # Clean up the story (remove quotes if wrapped)
            if story.startswith('"') and story.endswith('"'):
                story = story[1:-1]
            if story.startswith("'") and story.endswith("'"):
                story = story[1:-1]
            
            activity_stories[activity_id] = story
            stories_generated += 1
            print(f"   ✅ Generated new story for: {activity_name}")
            
            # Step 3: Save new story to Qdrant DB
            try:
                store_place_story(
                    place_name=activity_name,
                    story=story,
                    location=location,
                    activity_type=activity_type or "attraction",
                    metadata={
                        "activity_id": activity_id,
                        "description": activity_description
                    }
                )
                stories_saved += 1
                print(f"   💾 Saved story to Qdrant DB for: {activity_name}")
            except Exception as e:
                print(f"   ⚠️  Failed to save story to Qdrant for {activity_name}: {e}")
                # Continue even if save fails - story is still available in memory
            
        except Exception as e:
            print(f"   ⚠️  Failed to generate story for {activity_name}: {e}")
            # Continue with other activities even if one fails
            continue
    
    print(f"   📊 Summary: {stories_from_db} from DB, {stories_generated} generated, {stories_saved} saved to DB")
    print(f"   ✅ Total stories: {len(activity_stories)} out of {len(activities_options)} activities")
    
    return {
        "activity_stories": activity_stories,
        "messages": state.get("messages", []) + [f"Generated {len(activity_stories)} activity stories ({stories_from_db} from DB, {stories_generated} new)"]
    }


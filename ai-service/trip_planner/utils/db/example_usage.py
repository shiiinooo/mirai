"""
Example usage of the Qdrant database integration for place stories.

This script demonstrates how to:
1. Initialize Qdrant connection
2. Store place stories with automatic vectorization
3. Search for similar stories using semantic search
4. Retrieve stories by exact place name
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database functions
from trip_planner.utils.db import (
    init_qdrant,
    store_place_story,
    search_similar_stories,
    get_story_by_place,
    get_stories_by_location,
    check_qdrant_health
)


def example_store_stories():
    """Example: Store some place stories."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Storing Place Stories")
    print("="*80)
    
    # Example stories for popular tourist attractions
    stories = [
        {
            "place_name": "Eiffel Tower",
            "story": "An iconic iron lattice tower built in 1889, offering breathtaking views of Paris from its three observation levels. The tower sparkles with golden lights every evening, creating a magical atmosphere.",
            "location": "Paris, France",
            "activity_type": "landmark",
            "metadata": {
                "height_meters": 330,
                "year_built": 1889,
                "architect": "Gustave Eiffel"
            }
        },
        {
            "place_name": "Louvre Museum",
            "story": "The world's largest art museum, home to thousands of works including the Mona Lisa and Venus de Milo. Once a royal palace, it now houses masterpieces spanning from ancient civilizations to the 19th century.",
            "location": "Paris, France",
            "activity_type": "museum",
            "metadata": {
                "year_opened": 1793,
                "collections": ["Egyptian", "Greek", "Roman", "Renaissance"]
            }
        },
        {
            "place_name": "Senso-ji Temple",
            "story": "Tokyo's oldest and most significant Buddhist temple, founded in 628 AD. Visitors walk through the Thunder Gate and bustling Nakamise shopping street before reaching the main hall, where incense smoke is believed to have healing powers.",
            "location": "Tokyo, Japan",
            "activity_type": "temple",
            "metadata": {
                "year_founded": 628,
                "district": "Asakusa"
            }
        },
        {
            "place_name": "Tokyo Skytree",
            "story": "The tallest structure in Japan at 634 meters, offering panoramic views of Tokyo and Mount Fuji on clear days. The tower combines modern architecture with traditional Japanese aesthetics.",
            "location": "Tokyo, Japan",
            "activity_type": "landmark",
            "metadata": {
                "height_meters": 634,
                "year_built": 2012
            }
        }
    ]
    
    # Store each story
    for story in stories:
        try:
            story_id = store_place_story(
                place_name=story["place_name"],
                story=story["story"],
                location=story["location"],
                activity_type=story["activity_type"],
                metadata=story["metadata"]
            )
            print(f"  ✓ Stored: {story['place_name']} (ID: {story_id})")
        except Exception as e:
            print(f"  ✗ Failed to store {story['place_name']}: {e}")


def example_semantic_search():
    """Example: Search for similar stories using natural language."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Semantic Search")
    print("="*80)
    
    queries = [
        "ancient temple in Japan",
        "museum with famous paintings",
        "tall tower with city views"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            results = search_similar_stories(query, limit=3, score_threshold=0.5)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"\n  {i}. {result['place_name']} (Score: {result['score']:.2f})")
                    print(f"     Location: {result['location']}")
                    print(f"     Type: {result['activity_type']}")
                    print(f"     Story: {result['story'][:100]}...")
            else:
                print("  No results found")
        except Exception as e:
            print(f"  ✗ Search failed: {e}")


def example_exact_lookup():
    """Example: Get a story by exact place name."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Exact Place Lookup")
    print("="*80)
    
    place_names = [
        ("Eiffel Tower", "Paris, France"),
        ("Senso-ji Temple", "Tokyo, Japan"),
        ("Nonexistent Place", None)
    ]
    
    for place_name, location in place_names:
        print(f"\n📍 Looking up: '{place_name}'")
        try:
            story = get_story_by_place(place_name, location)
            
            if story:
                print(f"  ✓ Found!")
                print(f"    Location: {story['location']}")
                print(f"    Type: {story['activity_type']}")
                print(f"    Story: {story['story'][:100]}...")
            else:
                print(f"  ℹ️  No story found")
        except Exception as e:
            print(f"  ✗ Lookup failed: {e}")


def example_location_filter():
    """Example: Get all stories for a specific location."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Location-Based Retrieval")
    print("="*80)
    
    locations = ["Paris, France", "Tokyo, Japan"]
    
    for location in locations:
        print(f"\n🌍 Stories for: '{location}'")
        try:
            stories = get_stories_by_location(location, limit=10)
            
            if stories:
                print(f"  Found {len(stories)} stories:")
                for i, story in enumerate(stories, 1):
                    print(f"    {i}. {story['place_name']} ({story['activity_type']})")
            else:
                print(f"  No stories found for this location")
        except Exception as e:
            print(f"  ✗ Failed: {e}")


def main():
    """Run all examples."""
    print("\n" + "🌟"*40)
    print("QDRANT DATABASE INTEGRATION - EXAMPLE USAGE")
    print("🌟"*40)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in your .env file.")
        return
    
    # Initialize Qdrant
    print("\n🔧 Initializing Qdrant...")
    try:
        init_qdrant()
    except Exception as e:
        print(f"\n❌ Failed to initialize Qdrant: {e}")
        print("Make sure Qdrant is running (docker-compose up -d qdrant)")
        return
    
    # Check health
    if not check_qdrant_health():
        print("\n❌ Qdrant health check failed. Please check the service.")
        return
    
    print("\n✅ Qdrant is ready!\n")
    
    # Run examples
    try:
        example_store_stories()
        example_semantic_search()
        example_exact_lookup()
        example_location_filter()
    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✨ Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()


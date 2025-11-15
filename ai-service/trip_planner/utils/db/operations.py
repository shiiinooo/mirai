"""Database operations for place stories."""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

from .qdrant_client import get_qdrant_client
from .collections import PLACE_STORIES_COLLECTION
from .embeddings import generate_embedding, create_searchable_text


def store_place_story(
    place_name: str,
    story: str,
    location: str,
    activity_type: str = "attraction",
    metadata: Optional[Dict[str, Any]] = None,
    story_id: Optional[str] = None
) -> str:
    """
    Store a place story in Qdrant with automatic vectorization.
    
    Args:
        place_name: Name of the place (e.g., "Eiffel Tower")
        story: The story/description text to store
        location: Location in "City, Country" format (e.g., "Paris, France")
        activity_type: Type of place/activity (e.g., "museum", "restaurant", "attraction")
        metadata: Additional metadata dictionary
        story_id: Optional custom ID, generates UUID if not provided
    
    Returns:
        str: The ID of the stored story
    
    Raises:
        ValueError: If required fields are missing
        Exception: If storage fails
    """
    # Validate inputs
    if not place_name or not place_name.strip():
        raise ValueError("place_name is required")
    if not story or not story.strip():
        raise ValueError("story is required")
    if not location or not location.strip():
        raise ValueError("location is required")
    
    # Generate ID if not provided
    if not story_id:
        story_id = str(uuid.uuid4())
    
    # Prepare metadata
    full_metadata = metadata.copy() if metadata else {}
    full_metadata.update({
        "location": location,
        "activity_type": activity_type
    })
    
    # Create searchable text and generate embedding
    searchable_text = create_searchable_text(place_name, story, full_metadata)
    embedding = generate_embedding(searchable_text)
    
    # Prepare payload
    payload = {
        "place_name": place_name,
        "story": story,
        "location": location,
        "activity_type": activity_type,
        "created_at": datetime.utcnow().isoformat(),
        "metadata": full_metadata
    }
    
    # Store in Qdrant
    try:
        client = get_qdrant_client()
        point = PointStruct(
            id=story_id,
            vector=embedding,
            payload=payload
        )
        
        client.upsert(
            collection_name=PLACE_STORIES_COLLECTION,
            points=[point]
        )
        
        print(f"✅ Stored story for '{place_name}' (ID: {story_id})")
        return story_id
    
    except Exception as e:
        print(f"❌ Failed to store story: {e}")
        raise Exception(f"Failed to store place story: {e}")


def search_similar_stories(
    query: str,
    limit: int = 5,
    location_filter: Optional[str] = None,
    activity_type_filter: Optional[str] = None,
    score_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Search for similar place stories using semantic search.
    
    Args:
        query: Search query (place name or description)
        limit: Maximum number of results to return
        location_filter: Optional location filter ("City, Country")
        activity_type_filter: Optional activity type filter
        score_threshold: Minimum similarity score (0-1)
    
    Returns:
        List[Dict]: List of matching stories with scores and metadata
    
    Example:
        results = search_similar_stories(
            query="historic tower in Paris",
            limit=3,
            location_filter="Paris, France"
        )
    """
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Build filter conditions
        filter_conditions = []
        if location_filter:
            filter_conditions.append(
                FieldCondition(
                    key="location",
                    match=MatchValue(value=location_filter)
                )
            )
        if activity_type_filter:
            filter_conditions.append(
                FieldCondition(
                    key="activity_type",
                    match=MatchValue(value=activity_type_filter)
                )
            )
        
        # Create filter object if conditions exist
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Perform search
        client = get_qdrant_client()
        results = client.search(
            collection_name=PLACE_STORIES_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            query_filter=search_filter,
            score_threshold=score_threshold
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "place_name": result.payload.get("place_name"),
                "story": result.payload.get("story"),
                "location": result.payload.get("location"),
                "activity_type": result.payload.get("activity_type"),
                "created_at": result.payload.get("created_at"),
                "metadata": result.payload.get("metadata", {})
            })
        
        print(f"🔍 Found {len(formatted_results)} similar stories for query: '{query}'")
        return formatted_results
    
    except Exception as e:
        print(f"❌ Search failed: {e}")
        raise Exception(f"Failed to search stories: {e}")


def get_story_by_place(
    place_name: str,
    location: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a story by exact place name match.
    
    Args:
        place_name: Exact name of the place
        location: Optional location filter for disambiguation
    
    Returns:
        Dict or None: Story data if found, None otherwise
    """
    try:
        # Build filter
        filter_conditions = [
            FieldCondition(
                key="place_name",
                match=MatchValue(value=place_name)
            )
        ]
        
        if location:
            filter_conditions.append(
                FieldCondition(
                    key="location",
                    match=MatchValue(value=location)
                )
            )
        
        search_filter = Filter(must=filter_conditions)
        
        # Scroll to get matching points
        client = get_qdrant_client()
        results, _ = client.scroll(
            collection_name=PLACE_STORIES_COLLECTION,
            scroll_filter=search_filter,
            limit=1
        )
        
        if results:
            result = results[0]
            return {
                "id": result.id,
                "place_name": result.payload.get("place_name"),
                "story": result.payload.get("story"),
                "location": result.payload.get("location"),
                "activity_type": result.payload.get("activity_type"),
                "created_at": result.payload.get("created_at"),
                "metadata": result.payload.get("metadata", {})
            }
        
        print(f"ℹ️  No story found for place: '{place_name}'")
        return None
    
    except Exception as e:
        print(f"❌ Failed to get story by place: {e}")
        raise Exception(f"Failed to get story: {e}")


def delete_story(story_id: str) -> bool:
    """
    Delete a story by ID.
    
    Args:
        story_id: ID of the story to delete
    
    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        client = get_qdrant_client()
        client.delete(
            collection_name=PLACE_STORIES_COLLECTION,
            points_selector=[story_id]
        )
        print(f"🗑️  Deleted story: {story_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to delete story: {e}")
        return False


def get_stories_by_location(
    location: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get all stories for a specific location.
    
    Args:
        location: Location in "City, Country" format
        limit: Maximum number of stories to return
    
    Returns:
        List[Dict]: List of stories for the location
    """
    try:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="location",
                    match=MatchValue(value=location)
                )
            ]
        )
        
        client = get_qdrant_client()
        results, _ = client.scroll(
            collection_name=PLACE_STORIES_COLLECTION,
            scroll_filter=search_filter,
            limit=limit
        )
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "place_name": result.payload.get("place_name"),
                "story": result.payload.get("story"),
                "location": result.payload.get("location"),
                "activity_type": result.payload.get("activity_type"),
                "created_at": result.payload.get("created_at"),
                "metadata": result.payload.get("metadata", {})
            })
        
        print(f"📍 Found {len(formatted_results)} stories for location: '{location}'")
        return formatted_results
    
    except Exception as e:
        print(f"❌ Failed to get stories by location: {e}")
        raise Exception(f"Failed to get stories by location: {e}")


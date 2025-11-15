"""Qdrant collection schemas and setup."""

import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType, PayloadIndexInfo

# Collection name constant
PLACE_STORIES_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "place_stories")

# Vector configuration
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small dimension
DISTANCE_METRIC = Distance.COSINE


def ensure_collections_exist(client: QdrantClient):
    """
    Ensure all required collections exist in Qdrant.
    Creates collections if they don't exist.
    
    Args:
        client: QdrantClient instance
    """
    ensure_place_stories_collection(client)


def ensure_place_stories_collection(client: QdrantClient):
    """
    Ensure the place_stories collection exists.
    
    Collection schema:
    - Vectors: 1536 dimensions (OpenAI text-embedding-3-small)
    - Distance: Cosine similarity
    - Payload fields:
        - place_name: str (indexed) - Name of the place
        - story: str - The story/description text
        - location: str (indexed) - City, Country format
        - activity_type: str (indexed) - Type of activity/place
        - created_at: str - ISO timestamp
        - metadata: dict - Additional metadata
    
    Args:
        client: QdrantClient instance
    """
    collection_name = PLACE_STORIES_COLLECTION
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_exists = any(col.name == collection_name for col in collections)
    
    if not collection_exists:
        print(f"📦 Creating collection: {collection_name}")
        
        # Create collection with vector configuration
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=DISTANCE_METRIC
            )
        )
        
        # Create payload indexes for efficient filtering
        # Index place_name for exact matches
        client.create_payload_index(
            collection_name=collection_name,
            field_name="place_name",
            field_schema=PayloadSchemaType.KEYWORD
        )
        
        # Index location for filtering by city/country
        client.create_payload_index(
            collection_name=collection_name,
            field_name="location",
            field_schema=PayloadSchemaType.KEYWORD
        )
        
        # Index activity_type for filtering by type
        client.create_payload_index(
            collection_name=collection_name,
            field_name="activity_type",
            field_schema=PayloadSchemaType.KEYWORD
        )
        
        print(f"✅ Collection {collection_name} created successfully")
    else:
        print(f"✓ Collection {collection_name} already exists")


def get_collection_info(client: QdrantClient) -> dict:
    """
    Get information about the place_stories collection.
    
    Args:
        client: QdrantClient instance
    
    Returns:
        dict: Collection information including count and configuration
    """
    collection_name = PLACE_STORIES_COLLECTION
    
    try:
        info = client.get_collection(collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
            "config": {
                "vector_size": VECTOR_SIZE,
                "distance": DISTANCE_METRIC.value
            }
        }
    except Exception as e:
        return {
            "name": collection_name,
            "error": str(e),
            "exists": False
        }


# Qdrant Database Setup Guide

This guide will help you set up and use the Qdrant vector database integration in the Mirai trip planner project.

## Quick Start

### 1. Start Qdrant Database

From the project root directory, start the Qdrant service:

```bash
docker-compose up -d qdrant
```

Verify it's running:

```bash
docker ps | grep qdrant
```

You should see the `mirai-qdrant` container running.

### 2. Configure Environment Variables

Add these to your `ai-service/.env` file (create it if it doesn't exist):

```bash
# Required for embeddings
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Qdrant configuration (these are the defaults)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=place_stories
```

### 3. Install Python Dependencies

```bash
cd ai-service
pip install -r requirements.txt
```

### 4. Test the Integration

Run the example script to test the database:

```bash
python -m trip_planner.utils.db.example_usage
```

This will:
- Initialize the Qdrant connection
- Create the `place_stories` collection
- Store sample place stories
- Demonstrate semantic search
- Show filtering capabilities

## Using Qdrant in Your Code

### Basic Operations

```python
from trip_planner.utils.db import (
    init_qdrant,
    store_place_story,
    search_similar_stories,
    get_story_by_place
)

# Initialize (run once at startup)
init_qdrant()

# Store a story
story_id = store_place_story(
    place_name="Tokyo Skytree",
    story="The tallest structure in Japan at 634 meters...",
    location="Tokyo, Japan",
    activity_type="landmark",
    metadata={"height_meters": 634}
)

# Search semantically
results = search_similar_stories(
    query="tall observation tower in Tokyo",
    limit=5
)

# Get by exact name
story = get_story_by_place("Tokyo Skytree", location="Tokyo, Japan")
```

## API Integration

The Qdrant database is automatically initialized when the FastAPI app starts. You can access it from your API endpoints:

```python
from fastapi import APIRouter
from trip_planner.utils.db import search_similar_stories

router = APIRouter()

@router.get("/api/places/search")
async def search_places(query: str, location: str = None):
    results = search_similar_stories(
        query=query,
        location_filter=location,
        limit=10
    )
    return {"results": results}
```

## Accessing Qdrant Dashboard

Qdrant provides a web dashboard for exploring your data:

1. Make sure Qdrant is running: `docker-compose up -d qdrant`
2. Open your browser to: http://localhost:6333/dashboard
3. You can view collections, points, and run queries

## Common Operations

### View Collection Info

```python
from trip_planner.utils.db import get_qdrant_client
from trip_planner.utils.db.collections import get_collection_info

client = get_qdrant_client()
info = get_collection_info(client)
print(info)
```

### Delete a Story

```python
from trip_planner.utils.db.operations import delete_story

delete_story(story_id="your-story-id")
```

### Get All Stories for a Location

```python
from trip_planner.utils.db import get_stories_by_location

stories = get_stories_by_location("Paris, France", limit=20)
for story in stories:
    print(f"{story['place_name']}: {story['activity_type']}")
```

## Data Structure

Each place story contains:

```python
{
    "id": "uuid-string",
    "place_name": "Name of Place",
    "story": "Detailed description...",
    "location": "City, Country",
    "activity_type": "landmark|museum|restaurant|temple|...",
    "created_at": "2025-11-15T10:30:00",
    "metadata": {
        # Custom fields
        "height_meters": 330,
        "year_built": 1889,
        # ... any other data
    },
    "score": 0.95  # Only in search results
}
```

## Troubleshooting

### Connection Refused Error

**Problem**: `ConnectionError: Unable to connect to Qdrant`

**Solution**:
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not running, start it
docker-compose up -d qdrant

# Check logs
docker logs mirai-qdrant
```

### OpenAI API Errors

**Problem**: `ValueError: OPENAI_API_KEY environment variable is not set`

**Solution**: Add your OpenAI API key to `ai-service/.env`:
```bash
OPENAI_API_KEY=sk-...your-key-here
```

### Collection Not Found

**Problem**: `Collection 'place_stories' not found`

**Solution**: Run initialization:
```python
from trip_planner.utils.db import init_qdrant
init_qdrant()
```

### Empty Search Results

**Problem**: No results returned from semantic search

**Solutions**:
1. Lower the score threshold: `search_similar_stories(query, score_threshold=0.5)`
2. Check if data exists: Use `get_stories_by_location()` to list all stories
3. Verify embeddings are working: Check OpenAI API key and quota

## Docker Commands

```bash
# Start Qdrant
docker-compose up -d qdrant

# Stop Qdrant
docker-compose stop qdrant

# View logs
docker logs mirai-qdrant

# Restart Qdrant
docker-compose restart qdrant

# Remove Qdrant (WARNING: deletes all data)
docker-compose down -v qdrant
```

## Next Steps

1. **Story Creation Agent**: Implement an agent that generates stories for places visited in activities
2. **Integration**: Connect the database to the trip planner workflow to automatically retrieve stories
3. **Caching**: Add a caching layer for frequently accessed stories
4. **Batch Operations**: Implement bulk import/export for large datasets

## Documentation

- Detailed API documentation: [`ai-service/trip_planner/utils/db/README.md`](ai-service/trip_planner/utils/db/README.md)
- Qdrant official docs: https://qdrant.tech/documentation/
- OpenAI embeddings: https://platform.openai.com/docs/guides/embeddings

## Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application              │
│  (api.py - Auto-initializes on startup) │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      trip_planner.utils.db               │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  qdrant_client.py                  │ │
│  │  - Connection manager              │ │
│  │  - Health checks                   │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  embeddings.py                     │ │
│  │  - OpenAI text-embedding-3-small   │ │
│  │  - Batch operations                │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  operations.py                     │ │
│  │  - store_place_story()             │ │
│  │  - search_similar_stories()        │ │
│  │  - get_story_by_place()            │ │
│  └────────────────────────────────────┘ │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│          Qdrant Database                 │
│      (Docker Container: mirai-qdrant)    │
│                                          │
│  Collection: place_stories               │
│  - Vector size: 1536                     │
│  - Distance: Cosine                      │
│  - Indexes: place_name, location, type   │
└─────────────────────────────────────────┘
```

## Support

For issues or questions:
1. Check the [database README](ai-service/trip_planner/utils/db/README.md)
2. Review the [example usage](ai-service/trip_planner/utils/db/example_usage.py)
3. Check Qdrant logs: `docker logs mirai-qdrant`


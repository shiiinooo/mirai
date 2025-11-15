# Qdrant Database Integration

This module provides integration with Qdrant vector database for storing and retrieving place stories with semantic search capabilities.

## Features

- **Automatic Vectorization**: Text is automatically converted to embeddings using OpenAI's `text-embedding-3-small` model
- **Semantic Search**: Find similar places and stories using natural language queries
- **Metadata Filtering**: Filter results by location, activity type, and custom metadata
- **Easy to Use**: Simple API for storing and retrieving place stories

## Architecture

```
db/
├── __init__.py           # Module exports
├── qdrant_client.py      # Connection manager and client initialization
├── collections.py        # Collection schemas and setup
├── embeddings.py         # OpenAI embeddings service
├── operations.py         # CRUD operations for place stories
├── example_usage.py      # Usage examples
└── README.md            # This file
```

## Setup

### 1. Start Qdrant Database

Make sure Qdrant is running via Docker:

```bash
docker-compose up -d qdrant
```

### 2. Environment Variables

Set the following environment variables in your `.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Qdrant Configuration (defaults shown)
QDRANT_HOST=qdrant              # Docker service name or IP
QDRANT_PORT=6333                # HTTP API port
QDRANT_COLLECTION_NAME=place_stories
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Initialize Qdrant

```python
from trip_planner.utils.db import init_qdrant

# Initialize connection and ensure collections exist
init_qdrant()
```

### Store a Place Story

```python
from trip_planner.utils.db import store_place_story

story_id = store_place_story(
    place_name="Eiffel Tower",
    story="An iconic iron lattice tower built in 1889...",
    location="Paris, France",
    activity_type="landmark",
    metadata={
        "height_meters": 330,
        "year_built": 1889
    }
)
```

### Semantic Search

```python
from trip_planner.utils.db import search_similar_stories

# Natural language query
results = search_similar_stories(
    query="ancient temple in Japan",
    limit=5,
    location_filter="Tokyo, Japan",  # Optional
    activity_type_filter="temple",    # Optional
    score_threshold=0.7
)

for result in results:
    print(f"{result['place_name']}: {result['score']:.2f}")
    print(f"Story: {result['story']}")
```

### Get Story by Exact Name

```python
from trip_planner.utils.db import get_story_by_place

story = get_story_by_place(
    place_name="Eiffel Tower",
    location="Paris, France"  # Optional, for disambiguation
)

if story:
    print(story['story'])
```

### Get All Stories for a Location

```python
from trip_planner.utils.db import get_stories_by_location

stories = get_stories_by_location("Paris, France", limit=10)

for story in stories:
    print(f"- {story['place_name']} ({story['activity_type']})")
```

## Data Schema

### Place Story Structure

Each place story is stored with the following fields:

```python
{
    "place_name": str,        # Name of the place
    "story": str,             # The story/description
    "location": str,          # "City, Country" format
    "activity_type": str,     # e.g., "museum", "restaurant", "landmark"
    "created_at": str,        # ISO timestamp
    "metadata": dict          # Custom metadata
}
```

### Vector Configuration

- **Model**: OpenAI `text-embedding-3-small`
- **Dimensions**: 1536
- **Distance Metric**: Cosine similarity
- **Indexed Fields**: `place_name`, `location`, `activity_type`

## Example: Running the Demo

```bash
cd ai-service
python -m trip_planner.utils.db.example_usage
```

This will:
1. Initialize Qdrant connection
2. Store sample place stories
3. Demonstrate semantic search
4. Show exact lookups
5. Filter by location

## API Integration

The database is automatically initialized when the FastAPI app starts. You can use the database functions in your API endpoints:

```python
from fastapi import FastAPI
from trip_planner.utils.db import search_similar_stories

@app.get("/api/places/search")
async def search_places(query: str):
    results = search_similar_stories(query, limit=10)
    return {"results": results}
```

## Best Practices

1. **Searchable Text**: Combine place name, location, and key details for better embeddings
2. **Consistent Locations**: Use "City, Country" format for locations
3. **Activity Types**: Use consistent activity type labels (e.g., "museum", "temple", "landmark")
4. **Error Handling**: Wrap database calls in try-except blocks
5. **Batch Operations**: Use batch embedding functions for multiple texts

## Troubleshooting

### Connection Errors

If you see connection errors:

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Check Qdrant logs
docker logs mirai-qdrant

# Restart Qdrant
docker-compose restart qdrant
```

### OpenAI API Errors

- Verify `OPENAI_API_KEY` is set correctly
- Check API rate limits and quota
- Ensure you have access to the embedding model

### Empty Search Results

- Lower the `score_threshold` (default 0.7)
- Check if data is actually stored (use `get_collection_info`)
- Verify query text is meaningful

## Future Enhancements

- Caching layer for frequently accessed stories
- Bulk import/export utilities
- Advanced filtering and aggregations
- Integration with trip planner workflow
- Story creation agent


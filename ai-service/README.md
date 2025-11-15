# Trip Planner Multi-Agent System

A LangGraph-based AI-powered travel planning system using specialized agents that work in parallel to create personalized trip itineraries.

## 🏗️ Architecture

This system uses a **multi-agent workflow** with the following specialized agents:

### Data-Fetching Agents (Parallel Execution)
1. **Transport Agent** - Fetches real flight data via SerpAPI
2. **Accommodation Agent** - Fetches hotel options via SerpAPI
3. **Activities Agent** - Fetches activities and attractions
4. **Dining Agent** - Fetches restaurant options
5. **Key Phrases Agent** (LLM-Powered) - Generates essential phrases for destination language

### Decision Agents (LLM-Powered)
6. **Budget Coordinator Agent** - Intelligently selects best combination within budget
7. **Itinerary Generator Agent** - Creates structured day-by-day itinerary

## 📁 Project Structure

```
ai-service/
├── trip_planner/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── tools.py      # API integrations (SerpAPI for flights/hotels)
│   │   ├── state.py      # Graph state schema
│   │   ├── db/           # Qdrant vector database integration
│   │   │   ├── __init__.py
│   │   │   ├── qdrant_client.py    # Connection manager
│   │   │   ├── collections.py      # Collection schemas
│   │   │   ├── embeddings.py       # OpenAI embeddings
│   │   │   ├── operations.py       # CRUD operations
│   │   │   ├── example_usage.py    # Usage examples
│   │   │   └── README.md           # Database documentation
│   │   └── nodes/        # Individual agent node files
│   │       ├── __init__.py
│   │       ├── transport_node.py
│   │       ├── accommodation_node.py
│   │       ├── activities_node.py
│   │       ├── dining_node.py
│   │       ├── key_phrases_node.py
│   │       ├── budget_coordinator_node.py
│   │       └── itinerary_generator_node.py
│   ├── __init__.py
│   └── agent.py          # Graph construction and workflow
├── api.py                # FastAPI REST API server
├── transformers.py       # Data transformation utilities
├── main.py               # Entry point to run the planner
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── langgraph.json        # LangGraph configuration
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Docker and Docker Compose (for Qdrant database)

### Installation

1. **Create a virtual environment:**

```bash
cd ai-service
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
SERPAPI_API_KEY=your_serpapi_key_here

# Qdrant Vector Database (defaults work with Docker Compose)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=place_stories
```

4. **Start Qdrant Database (Docker):**

From the project root directory:

```bash
docker-compose up -d qdrant
```

This will start the Qdrant vector database for storing place stories.

### Running the Trip Planner

#### Option 1: As a REST API Server (Recommended for Integration)

Start the FastAPI server:

```bash
uvicorn api:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with the following endpoints:

- `GET /health` - Health check endpoint
- `POST /v1/trips/plan` - Generate a trip itinerary
- `GET /` - API information

**API Documentation**: Visit `http://localhost:8000/docs` for interactive API documentation.

#### Option 2: As a Standalone Script

Run the example trip planner script:

```bash
python main.py
```

This will run an example trip to Paris. The system will:
1. Search for transport, accommodation, activities, and restaurants (in parallel)
2. Select the best combination within budget
3. Generate a detailed day-by-day itinerary
4. Display and save the complete trip plan

## 📋 Usage

### Using the REST API

Send a POST request to `/v1/trips/plan` with the following JSON body:

```json
{
  "destination": "Tokyo, Japan",
  "startDate": "2024-12-15",
  "endDate": "2024-12-22",
  "tripType": "couple",
  "totalBudget": 3000,
  "currency": "USD",
  "comfortLevel": "standard",
  "preferredActivities": ["culture", "food", "nightlife"],
  "travelPace": "balanced",
  "mustSee": "Shibuya Crossing, teamLab Borderless"
}
```

**Response**: A complete Trip object with:
- Daily itineraries with morning/afternoon/evening schedules
- Budget breakdown by category
- Travel essentials (phrases, etiquette, packing list)
- Logistics (neighborhoods, transportation)

### Basic Usage (Programmatic)

```python
from trip_planner.agent import get_compiled_graph

# Define your trip requirements
trip_request = {
    "destination": "Paris, France",
    "origin": "New York, USA",
    "duration": 5,
    "budget": 3000,
    "preferred_activities": ["museums", "food", "culture"],
    "constraints": {
        "comfort_level": "mid",  # low, mid, or high
        "allergies": [],
        "walking_distance": 5  # km per day
    }
}

# Initialize state
initial_state = {
    **trip_request,
    "transport_options": [],
    "accommodation_options": [],
    "activities_options": [],
    "dining_options": [],
    "selected_transport": None,
    "selected_accommodation": None,
    "selected_activities": [],
    "selected_restaurants": [],
    "total_cost": 0.0,
    "remaining_budget": trip_request["budget"],
    "cost_breakdown": {},
    "requires_adjustment": False,
    "adjustment_iteration": 0,
    "max_iterations": 2,
    "final_itinerary": None,
    "messages": []
}

# Run the workflow
graph = get_compiled_graph()
result = graph.invoke(initial_state)

# Access the itinerary
itinerary = result["final_itinerary"]
```

### Customizing Trip Parameters

**Destination** (required): Any city or location
```python
"destination": "Tokyo, Japan"
```

**Origin** (optional): Starting location for transport search
```python
"origin": "Los Angeles, USA"
```

**Duration** (required): Trip length in days
```python
"duration": 7
```

**Budget** (required): Total budget in USD
```python
"budget": 4500
```

**Preferred Activities** (optional): List of interests
```python
"preferred_activities": [
    "museums", "food", "culture", "nightlife",
    "hiking", "adventure", "beaches", "shopping"
]
```

**Constraints** (optional): Additional preferences
```python
"constraints": {
    "comfort_level": "high",  # low, mid, or high
    "allergies": ["shellfish", "peanuts"],
    "walking_distance": 8  # km per day
}
```

## 🔄 Workflow

The system uses a **parallel architecture** for efficiency:

```
┌─────────────────────────────────────────────────┐
│                    START                        │
└─────────────────────────────────────────────────┘
          │
          ├─────────┬─────────┬─────────┐
          ▼         ▼         ▼         ▼
    ┌─────────┬─────────┬─────────┬─────────┐
    │Transport│ Accomm. │Activities│ Dining  │
    │  Node   │  Node   │  Node   │  Node   │
    └─────────┴─────────┴─────────┴─────────┘
          │         │         │         │
          └─────────┴─────────┴─────────┘
                    ▼
          ┌─────────────────────┐
          │ Budget Coordinator  │ (LLM)
          └─────────────────────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    Budget OK?          Budget Exceeded?
          │                   │
          │              (Loop back,
          │               max 2 times)
          ▼
    ┌─────────────────────┐
    │Itinerary Generator  │ (LLM)
    └─────────────────────┘
              │
              ▼
            END
```

### Key Features

- **Parallel Processing**: All research agents run simultaneously for speed
- **Budget-Aware**: Automatically adjusts selections to fit within budget
- **Smart Optimization**: LLM intelligently balances cost, quality, and preferences
- **Detailed Itineraries**: Day-by-day schedules with timing and explanations

## 🧪 Testing

Run tests with sample trips:

```bash
python main.py
```

The example includes three pre-configured trips:
1. Paris Adventure (5 days, $3000, mid-range)
2. Tokyo Adventure (7 days, $4500, luxury)
3. Barcelona Budget Trip (4 days, $1500, budget)

## 📦 Output

The system generates:

1. **Console Output**: Real-time progress and formatted itinerary
2. **JSON File**: Complete itinerary saved as `trip_itinerary.json`

### Output Structure

```json
{
  "itinerary": [
    {
      "day": 1,
      "date": "2024-06-15",
      "morning": {...},
      "lunch": {...},
      "afternoon": {...},
      "dinner": {...}
    }
  ],
  "transport": {...},
  "accommodation": {...},
  "selected_activities": [...],
  "selected_restaurants": [...],
  "cost_breakdown": {
    "transport": 450,
    "accommodation": 600,
    "activities": 300,
    "dining": 250,
    "total": 1600
  },
  "remaining_budget": 400,
  "tips": [...]
}
```

## 🔧 Configuration

### LangGraph Configuration (`langgraph.json`)

```json
{
  "dependencies": ["."],
  "graphs": {
    "trip_planner": "./trip_planner/agent.py:graph"
  },
  "env": ".env",
  "python_version": "3.11"
}
```

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: `gpt-4o-mini`)
- `SERPAPI_API_KEY`: Your SerpAPI key (required for real flight/hotel data)

## 🔌 Real API Integration

The system uses **SerpAPI** for real flight and hotel data:

1. **Flight Data**: Real-time flight search via SerpAPI Google Flights
   - Supports round-trip and one-way flights
   - Includes pricing, duration, stops, airline information
   - Provides booking links

2. **Hotel Data**: Real-time hotel search via SerpAPI Google Hotels
   - Hotel listings with prices, ratings, and amenities
   - Location-based recommendations
   - Booking information

3. **API Credentials** - Add to `.env`:
```
SERPAPI_API_KEY=your_serpapi_key_here
```

**Note**: Activities and dining still use mock data. To integrate real APIs for these:
- Activities: Google Places, TripAdvisor, Viator
- Restaurants: Google Places, Yelp

## 🗄️ Qdrant Vector Database

The system includes **Qdrant vector database** integration for storing and retrieving place stories with semantic search capabilities.

### Features

- **Automatic Vectorization**: Stories are automatically converted to embeddings using OpenAI's `text-embedding-3-small` model
- **Semantic Search**: Find similar places using natural language queries
- **Metadata Filtering**: Filter by location, activity type, and custom metadata
- **Persistent Storage**: Stories are saved across application restarts

### Usage Example

```python
from trip_planner.utils.db import (
    store_place_story,
    search_similar_stories,
    get_story_by_place
)

# Store a place story
story_id = store_place_story(
    place_name="Eiffel Tower",
    story="An iconic iron lattice tower built in 1889...",
    location="Paris, France",
    activity_type="landmark",
    metadata={"height_meters": 330, "year_built": 1889}
)

# Search for similar places
results = search_similar_stories(
    query="historic tower in Paris",
    limit=5,
    location_filter="Paris, France"
)

# Get story by exact name
story = get_story_by_place("Eiffel Tower", location="Paris, France")
```

### Running Database Examples

```bash
# Make sure Qdrant is running
docker-compose up -d qdrant

# Run the example script
python -m trip_planner.utils.db.example_usage
```

For detailed database documentation, see [`trip_planner/utils/db/README.md`](trip_planner/utils/db/README.md).

## 📝 Notes

- The system automatically handles budget adjustments (up to 2 iterations)
- Currency support: USD, EUR, GBP, JPY, AUD (default: EUR)
- Flight and hotel data comes from SerpAPI (real-time)
- Activities and dining use contextual mock data
- The LLM agents use OpenAI's function calling for structured outputs
- Round-trip flights are automatically detected and linked

## 🤝 Contributing

To extend the system:

1. Add new agent nodes in `utils/nodes/` directory
2. Update the state schema in `utils/state.py`
3. Modify the graph in `agent.py` to include new nodes
4. Add new API integrations in `utils/tools.py`

## 📄 License

See project root for license information.

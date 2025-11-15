"""
FastAPI REST API wrapper for the Trip Planner Multi-Agent System.

This API provides endpoints for generating personalized trip itineraries.
"""

import os
from datetime import datetime
from typing import List, Optional, Literal, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from io import BytesIO

from trip_planner.agent import get_compiled_graph
from transformers import transform_request_to_state, transform_result_to_trip
from trip_planner.utils.airports import search_airports
from trip_planner.utils.tts import generate_audio_from_text

# Load environment variables
load_dotenv()

# Verify OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not found in environment variables")

# Initialize FastAPI app
app = FastAPI(
    title="Trip Planner API",
    description="AI-powered trip planning service using multi-agent workflow",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    print("🚀 Starting Trip Planner API...")
    
    # Initialize Qdrant database
    try:
        from trip_planner.utils.db import init_qdrant, check_qdrant_health
        
        print("🔧 Initializing Qdrant database...")
        init_qdrant()
        
        if check_qdrant_health():
            print("✅ Qdrant database is ready")
        else:
            print("⚠️  Qdrant health check failed - vector DB features may not work")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize Qdrant: {e}")
        print("   Vector DB features will not be available")
    
    print("✅ API startup complete")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the compiled graph
graph = get_compiled_graph()

# In-memory cache for activity stories (trip_id -> activity_stories mapping)
# In production, this should be replaced with a proper database
activity_stories_cache: Dict[str, Dict[str, str]] = {}


# ============================================================================
# Pydantic Models (matching frontend format)
# ============================================================================

class TripPlanRequest(BaseModel):
    """Request model for trip planning - matches frontend TripPlanRequest."""
    destination: str = Field(..., description="Destination city/country")
    destinationAirportCode: Optional[str] = Field(None, description="Destination airport code (e.g., CDG)")
    origin: Optional[str] = Field(None, description="Origin city/country (current location)")
    originAirportCode: Optional[str] = Field(None, description="Origin airport code (e.g., JFK)")
    startDate: str = Field(..., description="Start date in YYYY-MM-DD format")
    endDate: str = Field(..., description="End date in YYYY-MM-DD format")
    tripType: Literal["solo", "couple", "friends", "family"] = Field(..., description="Type of trip")
    totalBudget: float = Field(..., description="Total budget for the trip")
    currency: str = Field(default="EUR", description="Currency code (USD, EUR, etc.)")
    comfortLevel: Literal["backpacker", "standard", "premium"] = Field(..., description="Accommodation comfort level")
    preferredActivities: List[str] = Field(..., description="List of preferred activities")
    travelPace: Literal["chill", "balanced", "packed"] = Field(..., description="Desired travel pace")
    mustSee: Optional[str] = Field(None, description="Must-see places or experiences")


class AirportSearchResult(BaseModel):
    """Airport search result."""
    code: str = Field(..., description="IATA airport code (3 letters)")
    name: str = Field(..., description="Airport name")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    displayName: str = Field(..., description="Display name (e.g., 'Paris - Charles de Gaulle (CDG)')")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/v1/airports/search", response_model=List[AirportSearchResult])
async def search_airports_endpoint(q: str):
    """
    Search for airports by city name or airport code.
    
    Args:
        q: Search query (city name, country, or airport code)
    
    Returns:
        List of matching airports
    
    Examples:
        - /v1/airports/search?q=paris
        - /v1/airports/search?q=new york
        - /v1/airports/search?q=CDG
    """
    try:
        results = search_airports(q)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search airports: {str(e)}"
        )


@app.post("/v1/trips/plan")
async def plan_trip(request: TripPlanRequest):
    """
    Generate a personalized trip itinerary.
    
    This endpoint:
    1. Transforms the frontend request to AI service format
    2. Runs the multi-agent workflow
    3. Transforms the result to frontend Trip format
    
    Returns:
        Trip object with complete itinerary, budget, essentials, and logistics
    """
    try:
        print(f"\n🌍 Received trip planning request for {request.destination}")
        
        # Transform request to internal state format
        initial_state = transform_request_to_state(request)
        
        print(f"🚀 Running multi-agent workflow...")
        
        # Run the graph workflow
        result = graph.invoke(initial_state)
        
        print(f"✅ Workflow completed successfully")
        
        # Transform result to frontend Trip format
        trip = transform_result_to_trip(result, request)
        
        # Store activity stories in cache for audio generation
        activity_stories = result.get("activity_stories", {})
        if activity_stories:
            activity_stories_cache[trip["id"]] = activity_stories
        
        print(f"📦 Returning trip itinerary")
        
        return trip
        
    except Exception as e:
        print(f"❌ Error planning trip: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trip plan: {str(e)}"
        )


@app.get("/v1/activities/{activity_id}/audio")
async def get_activity_audio(activity_id: str, trip_id: Optional[str] = None, story: Optional[str] = None):
    """
    Generate audio for an activity story using Eleven Labs TTS.
    
    Args:
        activity_id: The activity ID
        trip_id: Optional trip ID to look up story from cache
        story: Optional story text (if not provided, will try to fetch from cache)
    
    Returns:
        Audio stream (MP3 format)
    """
    try:
        # Get story text
        story_text = story
        
        # If story not provided, try to get from cache
        if not story_text and trip_id:
            activity_stories = activity_stories_cache.get(trip_id, {})
            story_text = activity_stories.get(activity_id)
        
        if not story_text:
            raise HTTPException(
                status_code=404,
                detail=f"Story not found for activity {activity_id}. Provide story text or valid trip_id."
            )
        
        # Generate audio
        try:
            audio_bytes = generate_audio_from_text(story_text)
        except ValueError as e:
            # API key not set
            raise HTTPException(
                status_code=500,
                detail=f"TTS service not configured: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate audio: {str(e)}"
            )
        
        # Return audio as streaming response
        audio_stream = BytesIO(audio_bytes)
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=activity_{activity_id}.mp3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate activity audio: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Trip Planner API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "plan_trip": "/v1/trips/plan (POST)",
            "activity_audio": "/v1/activities/{activity_id}/audio (GET)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# SerpAPI Dynamic Integration

## Overview

The trip planner now uses **SerpAPI** to dynamically fetch real-time data for:
- ✅ **Restaurants** (including coffee shops, cafes, and dining)
- ✅ **Tourist Activities** (attractions, tours, museums, events)
- ✅ **Hotels** (already integrated)
- ✅ **Flights** (already integrated)

## What Changed?

### 1. **Dynamic Restaurant & Coffee Shop Search**

Instead of static mock data, the system now:
- Searches for **best restaurants** in the destination
- Finds **coffee shops** and cafes
- Searches by **cuisine preferences** if specified
- Returns real ratings, reviews, prices, and locations

### 2. **Dynamic Tourist Activities**

The system now searches for:
- **Top attractions** (monuments, landmarks, museums)
- **Things to do** (tours, experiences)
- **Events** (concerts, festivals, happenings)
- **Preference-based activities** (hiking, nightlife, culture, etc.)

## API Endpoints Used

### Google Local API (for restaurants & attractions)
```python
{
    "engine": "google_local",
    "q": "Coffee shops in Paris",  # Customizable
    "location": "Paris, France",
    "hl": "en",  # Language
    "gl": "us",  # Country
}
```

### Google Events API (for tourist activities)
```python
{
    "engine": "google_events",
    "q": "Events in Paris",
    "hl": "en",
    "gl": "us",
    "htichips": "date:today"  # Optional filters
}
```

## Customization Parameters

### For Restaurants (`search_restaurants`)

**Query Customization:**
```python
constraints = {
    "max_daily_food_budget": 50,  # Max cost per person
    "dietary_restrictions": ["vegetarian", "gluten-free"],
    "cuisine_preferences": ["Italian", "Japanese"]
}

preferred_activities = [
    "Italian cuisine",
    "French food",
    "Local dining"
]
```

**What gets searched:**
- `"Best restaurants in {destination}"`
- `"Coffee shops in {destination}"`
- `"{cuisine} in {destination}"` (for each preference)

### For Activities (`search_activities`)

**Query Customization:**
```python
constraints = {
    "max_activity_price": 50,  # Maximum price per activity
    "activity_types": ["outdoor", "cultural"]
}

preferred_activities = [
    "museums",           # → searches "museums in {destination}"
    "nightlife",         # → searches "nightlife in {destination}"
    "adventure",         # → searches "adventure activities in {destination}"
    "hiking",            # → searches "hiking trails in {destination}"
    "culture",           # → searches "cultural sites in {destination}"
    "shopping",          # → searches "shopping in {destination}"
]
```

**What gets searched:**
- `"Top attractions in {destination}"`
- `"Things to do in {destination}"`
- `"{activity_type} in {destination}"` (based on preferences)
- `"Events in {destination}"` (via Google Events API)

## Activity Type Mapping

| Preference Keyword | Search Query |
|-------------------|--------------|
| `museums` | "museums in {destination}" |
| `culture` | "cultural sites in {destination}" |
| `nightlife` | "nightlife in {destination}" |
| `adventure` | "adventure activities in {destination}" |
| `outdoor` | "outdoor activities in {destination}" |
| `hiking` | "hiking trails in {destination}" |
| `shopping` | "shopping in {destination}" |
| `art` | "art galleries in {destination}" |
| `history` | "historical sites in {destination}" |
| `nature` | "nature parks in {destination}" |

## Usage Examples

### Example 1: Food Lover Trip
```python
state = {
    "destination": "Tokyo, Japan",
    "preferred_activities": [
        "Japanese cuisine",
        "Sushi restaurants",
        "Local food markets",
        "Coffee shops"
    ],
    "constraints": {
        "max_daily_food_budget": 75,
        "dietary_restrictions": ["no peanuts"]
    }
}

# Will search:
# - "Best restaurants in Tokyo"
# - "Coffee shops in Tokyo"
# - "Japanese cuisine in Tokyo"
# - "Sushi restaurants in Tokyo"
```

### Example 2: Adventure & Culture Trip
```python
state = {
    "destination": "Barcelona, Spain",
    "preferred_activities": [
        "museums",
        "culture",
        "nightlife",
        "outdoor activities"
    ],
    "constraints": {
        "max_activity_price": 40
    }
}

# Will search:
# - "Top attractions in Barcelona"
# - "Things to do in Barcelona"
# - "museums in Barcelona"
# - "cultural sites in Barcelona"
# - "nightlife in Barcelona"
# - "outdoor activities in Barcelona"
# - "Events in Barcelona"
```

### Example 3: Family Trip with Kids
```python
state = {
    "destination": "Orlando, Florida",
    "preferred_activities": [
        "family activities",
        "parks",
        "kid-friendly restaurants"
    ],
    "constraints": {
        "max_daily_food_budget": 30,
        "max_activity_price": 100,
        "family_friendly": True
    }
}

# Will search:
# - "Best restaurants in Orlando"
# - "Family restaurants in Orlando"
# - "Top attractions in Orlando"
# - "Things to do in Orlando"
# - "Parks in Orlando"
# - "Events in Orlando"
```

## Advanced Parameters

### Restaurant Search Options
```python
# In _search_local_serpapi function:
params = {
    "engine": "google_local",
    "q": query,           # What to search
    "location": location, # Where to search
    "hl": "en",          # Language: en, es, fr, de, etc.
    "gl": "us",          # Country: us, uk, fr, de, etc.
    "type": None,        # Type filter (optional)
}
```

### Events Search Options
```python
# In _search_events_serpapi function:
params = {
    "engine": "google_events",
    "q": query,
    "hl": "en",
    "gl": "us",
    "htichips": None,    # Filters: "date:today", "date:tomorrow", 
                         # "date:this_weekend", "event_type:Virtual-Event"
}
```

## Response Data Structure

### Restaurant Response
```python
{
    "id": "restaurant_12345",
    "name": "Le Bernardin",
    "cuisine": "French",
    "rating": 4.8,
    "reviews": 1250,
    "price_level": "$$$$",
    "avg_cost_per_person": 100,
    "meal_types": ["Lunch", "Dinner"],
    "location": "123 Main St",
    "reservations": "Required",
    "link": "https://...",
    "phone": "+1234567890",
    "latitude": 40.7580,
    "longitude": -73.9855
}
```

### Activity Response
```python
{
    "id": "activity_67890",
    "name": "Louvre Museum",
    "type": "Museum",
    "duration": "2-3 hours",
    "price": 20,
    "rating": 4.7,
    "reviews": 15000,
    "location": "Rue de Rivoli, Paris",
    "best_time": "Morning",
    "booking_required": True,
    "description": "World's largest art museum...",
    "link": "https://...",
    "latitude": 48.8606,
    "longitude": 2.3376
}
```

### Event Response
```python
{
    "id": "event_11223",
    "name": "Jazz Festival 2024",
    "type": "Event",
    "duration": "2-3 hours",
    "price": 0,
    "rating": 4.5,
    "reviews": 500,
    "location": "Central Park",
    "best_time": "Friday, Oct 15, 7-9 PM",
    "booking_required": True,
    "description": "Annual jazz festival...",
    "link": "https://...",
    "thumbnail": "https://..."
}
```

## Environment Setup

Make sure you have your SerpAPI key set:

```bash
export SERPAPI_API_KEY="your_serpapi_key_here"
```

Or in your `.env` file:
```
SERPAPI_API_KEY=your_serpapi_key_here
```

## Error Handling

The functions will raise `RuntimeError` if:
- SerpAPI key is not set
- API request fails
- API returns non-success status

Example:
```python
try:
    restaurants = search_restaurants(destination, preferences, constraints)
except RuntimeError as e:
    print(f"Failed to fetch restaurants: {e}")
    # Fallback to cached or default data
```

## Rate Limits

SerpAPI has rate limits based on your plan:
- Free: 100 searches/month
- Starter: 5,000 searches/month
- Developer: 15,000 searches/month

Each function call makes **multiple API requests**:
- `search_restaurants`: 2-4 requests (restaurants + coffee shops + cuisines)
- `search_activities`: 5-7 requests (attractions + things to do + events + preferences)

## Tips for Customization

1. **Be specific with preferences**: Instead of "food", use "Italian cuisine" or "Seafood restaurants"
2. **Use location hints**: "Downtown" vs "Near beach" in preferences
3. **Set budget constraints**: Filters results to match traveler's budget
4. **Combine preferences**: Mix activity types for diverse results
5. **Use language/country params**: `hl` and `gl` for localized results

## Future Enhancements

Potential improvements:
- [ ] Add time-based filtering (morning/evening activities)
- [ ] Distance-based filtering (within X km of hotel)
- [ ] Accessibility filters (wheelchair accessible, kid-friendly)
- [ ] Real-time availability checking
- [ ] Review sentiment analysis
- [ ] Price trend analysis

---

**Last Updated**: November 2025  
**Integration Status**: ✅ Complete


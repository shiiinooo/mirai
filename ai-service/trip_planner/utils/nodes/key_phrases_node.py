"""Key Phrases Node - Uses LLM to generate essential phrases for the destination language."""

from typing import Dict, Any
import json
from langchain_core.messages import SystemMessage, HumanMessage

from tracing import observe
from ..state import TripPlannerState
from ..llm_utils import get_llm
from ..json_parser import safe_parse_llm_json_response


@observe(name="key_phrases_node")
def key_phrases_node(state: TripPlannerState) -> Dict[str, Any]:
    """
    Key Phrases Generator Agent - Uses LLM to generate essential phrases 
    for the destination country's language.
    """
    print("\n🗣️  Key Phrases Node: Generating essential phrases...")
    
    # Initialize LLM
    # Initialize LLM (Mistral with OpenAI fallback) - higher temperature for creative content
    llm = get_llm(temperature=0.7)
    
    destination = state["destination"]
    
    # Extract country from destination (e.g., "Paris, France" -> "France")
    country = destination.split(",")[-1].strip() if "," in destination else destination
    
    # Build prompt
    system_prompt = """You are a language learning assistant for travelers. Generate essential key phrases 
that travelers should know when visiting a specific country.

For each phrase, provide:
1. The English phrase
2. The translation in the local language
3. Phonetic pronunciation guide (how to say it)

Return a JSON object with this exact structure:
{
    "language": "Language name (e.g., Japanese, French, Spanish)",
    "phrases": [
        {
            "english": "Hello",
            "translation": "Konnichiwa",
            "phonetic": "kon-nee-chee-wah"
        },
        {
            "english": "Thank you",
            "translation": "Arigatou gozaimasu",
            "phonetic": "ah-ree-gah-toh go-zai-mas"
        }
    ]
}

Include these essential phrases:
- Greetings (Hello, Goodbye, Good morning, Good evening)
- Politeness (Please, Thank you, Excuse me, Sorry)
- Common questions (How much?, Where is...?, Do you speak English?)
- Emergency/Help (Help, I need a doctor, I'm lost)
- Basic needs (Water, Food, Bathroom, Yes, No)
- Numbers (1-10 if relevant)

Generate 10-15 most useful phrases for travelers.
"""
    
    user_prompt = f"""
Generate essential key phrases for travelers visiting: {destination}

Country: {country}

Create practical, commonly-used phrases that will help travelers communicate 
during their trip. Focus on phrases that are most likely to be needed in 
everyday situations like ordering food, asking directions, shopping, etc.
"""
    
    # Call LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    # Parse response using robust JSON parser
    try:
        phrases_data = safe_parse_llm_json_response(response.content)
        
        print(f"   ✅ Generated {len(phrases_data.get('phrases', []))} key phrases in {phrases_data.get('language', 'unknown language')}")
        
        return {
            "key_phrases": phrases_data,
            "messages": state.get("messages", []) + ["Key phrases generated"]
        }
        
    except Exception as e:
        print(f"   Error parsing key phrases: {e}")
        # Fallback: return basic structure
        fallback_phrases = {
            "language": "Unknown",
            "phrases": [
                {
                    "english": "Hello",
                    "translation": "Hello",
                    "phonetic": "heh-loh"
                },
                {
                    "english": "Thank you",
                    "translation": "Thank you",
                    "phonetic": "thank yoo"
                }
            ]
        }
        
        return {
            "key_phrases": fallback_phrases,
            "messages": state.get("messages", []) + ["Key phrases generated (fallback)"]
        }


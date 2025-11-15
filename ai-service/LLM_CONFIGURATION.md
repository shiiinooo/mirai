# LLM Configuration Guide

## Overview

The Trip Planner AI service now uses **Mistral** as the primary LLM provider with **OpenAI** as an automatic fallback. This provides cost optimization and flexibility.

---

## Priority Order

1. **Mistral** (Primary) - Used if `MISTRAL_API_KEY` is set
2. **OpenAI** (Fallback) - Used if Mistral fails or key is missing

---

## Environment Variables

### Required (at least one)

```env
# Mistral API Key (Primary)
MISTRAL_API_KEY=your_mistral_api_key_here

# OpenAI API Key (Fallback)
OPENAI_API_KEY=your_openai_api_key_here
```

### Optional Model Overrides

```env
# Override default Mistral model (default: mistral-large-latest)
MISTRAL_MODEL=mistral-medium-latest

# Override default OpenAI model (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o
```

---

## How It Works

### Automatic Fallback Logic

```python
from trip_planner.utils.llm_utils import get_llm

# Get LLM with automatic fallback
llm = get_llm(temperature=0.3)
# -> Tries Mistral first, falls back to OpenAI if needed
```

### Architecture

All nodes use a centralized LLM utility (`llm_utils.py`) that handles:

1. **API Key Detection** - Checks for Mistral key first
2. **Library Import** - Dynamically imports the correct library
3. **Initialization** - Creates the LLM instance with proper config
4. **Fallback** - Automatically tries OpenAI if Mistral fails
5. **Error Handling** - Raises clear errors if neither works

---

## Nodes Using LLM

All nodes now use the unified `get_llm()` utility:

### Filtering Nodes (temperature=0.3)
- **Activities Node** - Selects top 10 activities
- **Accommodation Node** - Selects top 10 hotels
- **Dining Node** - Selects top 10 restaurants
- **Transport Node** - Selects top 10 flights

### Coordination Node (temperature=0.3)
- **Budget Coordinator Node** - Optimizes budget allocation

### Creative Nodes (temperature=0.7)
- **Itinerary Generator Node** - Creates day-by-day schedule
- **Key Phrases Node** - Generates local language phrases

---

## Installation

### Install Mistral (Primary)

```bash
pip install langchain-mistralai>=0.2.0
```

### Already Installed (Fallback)

```bash
pip install langchain-openai>=0.2.0
```

### Full Install

```bash
pip install -r requirements.txt
```

---

## Cost Optimization

### Why Mistral First?

1. **Better pricing** - Mistral is generally more cost-effective
2. **High quality** - Mistral models perform excellently for travel planning
3. **Flexibility** - Easy to switch models via environment variables

### Estimated Costs Per Request

| Task | Mistral | OpenAI |
|------|---------|--------|
| Activity Selection | ~$0.001 | ~$0.002 |
| Hotel Selection | ~$0.001 | ~$0.002 |
| Dining Selection | ~$0.001 | ~$0.002 |
| Transport Selection | ~$0.001 | ~$0.002 |
| Budget Coordination | ~$0.002 | ~$0.004 |
| Itinerary Generation | ~$0.003 | ~$0.006 |
| **Total per trip** | **~$0.009** | **~$0.018** |

*Prices are approximate and vary by model version*

---

## Testing

### Test with Mistral Only

```bash
export MISTRAL_API_KEY=your_key_here
unset OPENAI_API_KEY
python -m trip_planner.utils.nodes.activities_node
```

### Test with OpenAI Only (Fallback)

```bash
unset MISTRAL_API_KEY
export OPENAI_API_KEY=your_key_here
python -m trip_planner.utils.nodes.activities_node
```

### Test Fallback Behavior

```bash
export MISTRAL_API_KEY=invalid_key
export OPENAI_API_KEY=your_real_openai_key
# Should see: "[LLM] Failed to initialize Mistral... falling back to OpenAI"
```

---

## Troubleshooting

### Error: "No LLM API keys found"

**Solution:** Set at least one API key:
```bash
export MISTRAL_API_KEY=your_key_here
# OR
export OPENAI_API_KEY=your_key_here
```

### Error: "Failed to initialize Mistral"

**Causes:**
1. Invalid API key
2. Missing `langchain-mistralai` library
3. Network/API issues

**Solution:** System will automatically fall back to OpenAI. Check logs for details.

### Mistral Not Being Used

**Check:**
1. Is `MISTRAL_API_KEY` set? `echo $MISTRAL_API_KEY`
2. Is library installed? `pip show langchain-mistralai`
3. Check logs for "[LLM] Using Mistral" vs "[LLM] Using OpenAI"

---

## Advanced Configuration

### Custom LLM Selection

```python
from trip_planner.utils.llm_utils import get_llm

# Force specific model
llm = get_llm(temperature=0.5, model_override="mistral-medium-latest")
```

### Extending to Other Providers

Edit `ai-service/trip_planner/utils/llm_utils.py`:

```python
def get_llm(temperature: float = 0.3):
    # Try your provider first
    if os.getenv("YOUR_PROVIDER_API_KEY"):
        # Initialize your provider
        pass
    
    # Then Mistral
    if os.getenv("MISTRAL_API_KEY"):
        # ...existing code...
    
    # Finally OpenAI fallback
    # ...existing code...
```

---

## Production Recommendations

1. **Set Both Keys** - For maximum reliability
2. **Monitor Usage** - Track which provider is being used
3. **Set Model Overrides** - Pin specific versions for consistency
4. **Rate Limiting** - Implement if making many requests
5. **Caching** - Cache LLM results for identical queries

---

## Getting API Keys

### Mistral

1. Go to https://console.mistral.ai/
2. Create an account
3. Navigate to API Keys
4. Generate a new key

### OpenAI

1. Go to https://platform.openai.com/
2. Create an account
3. Navigate to API Keys
4. Generate a new key

---

## Summary

✅ **Zero code changes needed** - Just set environment variables  
✅ **Automatic fallback** - No manual intervention required  
✅ **Cost optimized** - Uses cheaper Mistral by default  
✅ **Fully backwards compatible** - OpenAI still works  
✅ **Flexible** - Easy to switch providers or models  
✅ **DRY principle** - Single utility function for all nodes  

The system will always work as long as **at least one** API key is configured!


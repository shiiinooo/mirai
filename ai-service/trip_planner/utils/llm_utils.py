"""LLM utility functions for initializing language models with fallback support."""

import os
from typing import Optional


def get_llm(temperature: float = 0.3, model_override: Optional[str] = None):
    """
    Get an LLM instance with Mistral as default and OpenAI as fallback.
    
    Priority:
    1. Mistral (if MISTRAL_API_KEY is set)
    2. OpenAI (fallback if Mistral fails or key is missing)
    
    Args:
        temperature: Temperature parameter for the LLM (default: 0.3)
        model_override: Optional model name override
    
    Returns:
        LLM instance (either Mistral or OpenAI)
    
    Raises:
        RuntimeError: If neither Mistral nor OpenAI API keys are available
    """
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Try Mistral first
    if mistral_api_key:
        try:
            from langchain_mistralai import ChatMistralAI
            
            model_name = model_override or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
            
            llm = ChatMistralAI(
                model=model_name,
                temperature=temperature,
                mistral_api_key=mistral_api_key
            )
            
            print(f"   [LLM] Using Mistral ({model_name})")
            return llm
            
        except ImportError:
            print("   [LLM] Mistral library not installed, falling back to OpenAI")
        except Exception as e:
            print(f"   [LLM] Failed to initialize Mistral: {e}, falling back to OpenAI")
    
    # Fallback to OpenAI
    if openai_api_key:
        try:
            from langchain_openai import ChatOpenAI
            
            model_name = model_override or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            llm = ChatOpenAI(
                model=model_name,
                temperature=temperature
            )
            
            print(f"   [LLM] Using OpenAI ({model_name})")
            return llm
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI LLM: {e}")
    
    # No API keys available
    raise RuntimeError(
        "No LLM API keys found. Set either MISTRAL_API_KEY or OPENAI_API_KEY in your .env file"
    )


def get_llm_for_coordinator(temperature: float = 0.3):
    """
    Get LLM instance specifically for budget coordinator.
    Uses same fallback logic as get_llm().
    
    Args:
        temperature: Temperature parameter for the LLM (default: 0.3)
    
    Returns:
        LLM instance
    """
    return get_llm(temperature=temperature)


def get_llm_for_filtering(temperature: float = 0.3):
    """
    Get LLM instance for filtering nodes (activities, dining, accommodation, transport).
    Uses same fallback logic as get_llm().
    
    Args:
        temperature: Temperature parameter for the LLM (default: 0.3)
    
    Returns:
        LLM instance
    """
    return get_llm(temperature=temperature)


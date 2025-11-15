"""OpenAI embeddings service for text vectorization."""

import os
from typing import List, Union
from openai import OpenAI

# Initialize OpenAI client
_openai_client = None

# Embedding model configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def get_openai_client() -> OpenAI:
    """
    Get or create OpenAI client instance (singleton pattern).
    
    Returns:
        OpenAI: OpenAI client instance
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _openai_client = OpenAI(api_key=api_key)
    
    return _openai_client


def generate_embedding(text: str, model: str = EMBEDDING_MODEL) -> List[float]:
    """
    Generate embedding vector for a single text string.
    
    Args:
        text: Text to embed
        model: OpenAI embedding model to use (default: text-embedding-3-small)
    
    Returns:
        List[float]: Embedding vector of size 1536
    
    Raises:
        ValueError: If text is empty
        Exception: If OpenAI API call fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    try:
        client = get_openai_client()
        response = client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        raise Exception(f"Failed to generate embedding: {e}")


def generate_embeddings_batch(
    texts: List[str],
    model: str = EMBEDDING_MODEL
) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single API call.
    More efficient than calling generate_embedding multiple times.
    
    Args:
        texts: List of texts to embed
        model: OpenAI embedding model to use (default: text-embedding-3-small)
    
    Returns:
        List[List[float]]: List of embedding vectors
    
    Raises:
        ValueError: If texts list is empty or contains empty strings
        Exception: If OpenAI API call fails
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")
    
    # Filter out empty strings
    valid_texts = [t for t in texts if t and t.strip()]
    if not valid_texts:
        raise ValueError("All texts are empty")
    
    if len(valid_texts) != len(texts):
        print(f"⚠️  Warning: Filtered out {len(texts) - len(valid_texts)} empty texts")
    
    try:
        client = get_openai_client()
        response = client.embeddings.create(
            input=valid_texts,
            model=model
        )
        # Sort by index to maintain order
        sorted_embeddings = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_embeddings]
    except Exception as e:
        print(f"❌ Error generating batch embeddings: {e}")
        raise Exception(f"Failed to generate batch embeddings: {e}")


def create_searchable_text(place_name: str, story: str, metadata: dict = None) -> str:
    """
    Create a comprehensive searchable text by combining place info.
    This text will be embedded for semantic search.
    
    Args:
        place_name: Name of the place
        story: Story/description of the place
        metadata: Additional metadata (location, activity_type, etc.)
    
    Returns:
        str: Combined text optimized for embedding
    """
    parts = [place_name, story]
    
    if metadata:
        if "location" in metadata:
            parts.insert(1, f"Location: {metadata['location']}")
        if "activity_type" in metadata:
            parts.append(f"Type: {metadata['activity_type']}")
    
    return " | ".join(parts)


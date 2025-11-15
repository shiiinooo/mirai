"""Qdrant client connection manager."""

import os
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

# Global client instance
_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_config() -> dict:
    """
    Get Qdrant configuration from environment variables.
    
    Defaults to 'localhost' for local development (outside Docker)
    and 'qdrant' for Docker container networking.
    
    Returns:
        dict: Configuration dictionary with host and port
    """
    # Default to localhost for local dev, qdrant for Docker
    default_host = os.getenv("QDRANT_HOST", "localhost")
    return {
        "host": default_host,
        "port": int(os.getenv("QDRANT_PORT", "6333")),
    }


def get_qdrant_client() -> QdrantClient:
    """
    Get or create a Qdrant client instance (singleton pattern).
    
    Automatically tries localhost first (for local development), then falls back
    to 'qdrant' (for Docker) if localhost fails.
    
    Returns:
        QdrantClient: Connected Qdrant client
    
    Raises:
        ConnectionError: If unable to connect to Qdrant
    """
    global _qdrant_client
    
    if _qdrant_client is None:
        config = get_qdrant_config()
        
        # Always try localhost first (for local development), then the configured host
        # This allows local dev to work even if .env has QDRANT_HOST=qdrant
        hosts_to_try = ["localhost"]
        
        # Add the configured host if it's different from localhost
        if config["host"] != "localhost":
            hosts_to_try.append(config["host"])
        
        # Also try 'qdrant' if not already in the list (for Docker)
        if "qdrant" not in hosts_to_try:
            hosts_to_try.append("qdrant")
        
        last_error = None
        for host in hosts_to_try:
            try:
                print(f"[DEBUG] Trying to connect to Qdrant at {host}:{config['port']}...")
                _qdrant_client = QdrantClient(
                    host=host,
                    port=config["port"],
                    timeout=5
                )
                # Test connection
                _qdrant_client.get_collections()
                print(f"Connected to Qdrant at {host}:{config['port']}")
                return _qdrant_client
            except Exception as e:
                print(f"[DEBUG] Failed to connect to {host}:{config['port']}: {e}")
                last_error = e
                if _qdrant_client:
                    _qdrant_client = None
                # Continue to next host
                continue
        
        # If all hosts failed, raise error
        raise ConnectionError(
            f"Unable to connect to Qdrant. Tried hosts: {hosts_to_try}. "
            f"Last error: {last_error}"
        )
    
    return _qdrant_client


def check_qdrant_health() -> bool:
    """
    Check if Qdrant is accessible and healthy.
    
    Returns:
        bool: True if Qdrant is healthy, False otherwise
    """
    try:
        client = get_qdrant_client()
        client.get_collections()
        return True
    except Exception as e:
        print(f"[WARNING] Qdrant health check failed: {e}")
        return False


def init_qdrant():
    """
    Initialize Qdrant connection and ensure collections exist.
    Call this on application startup.
    """
    from .collections import ensure_collections_exist
    
    try:
        client = get_qdrant_client()
        print("[INFO] Initializing Qdrant collections...")
        ensure_collections_exist(client)
        print("[SUCCESS] Qdrant initialization complete")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Qdrant: {e}")
        raise


def reset_client():
    """Reset the global client instance (useful for testing)."""
    global _qdrant_client
    _qdrant_client = None


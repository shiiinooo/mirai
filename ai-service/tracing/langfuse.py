"""
Simple Langfuse tracing module for AI service agents.

This module provides a simple @observe() decorator for tracing agent steps.

Simply add @observe() to any function you want to trace.

Usage:

    from tracing.langfuse import observe

    

    @observe()

    def my_agent_function(input_data):

        # Your function logic here

        return result

"""

import os
from functools import wraps
from typing import Callable, Optional
from inspect import iscoroutinefunction

try:
    from langfuse import observe as langfuse_observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("Warning: Langfuse not installed. Tracing will be disabled.")


def observe(name: Optional[str] = None):
    """
    Simple decorator for tracing function execution with Langfuse.
    
    Args:
        name: Custom name for the trace/span
            
    Returns:
        Decorated function with tracing enabled (or no-op if not configured)
    """
    
    # Get Langfuse configuration from environment variables
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # Check if Langfuse is properly configured
    if not LANGFUSE_AVAILABLE or not public_key or not secret_key:
        # Return a no-op decorator if not configured
        def noop_decorator(func: Callable) -> Callable:
            # Handle async functions properly
            if iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return sync_wrapper
        return noop_decorator
    
    # Initialize Langfuse client if not already initialized
    # The observe decorator will use environment variables automatically,
    # but we can also initialize explicitly if needed
    try:
        # Langfuse observe decorator automatically uses environment variables
        # so we can just return it directly
        return langfuse_observe(name=name)
    except Exception as e:
        # If initialization fails, return no-op decorator
        print(f"Warning: Failed to initialize Langfuse: {e}. Tracing will be disabled.")
        def noop_decorator(func: Callable) -> Callable:
            if iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return sync_wrapper
        return noop_decorator


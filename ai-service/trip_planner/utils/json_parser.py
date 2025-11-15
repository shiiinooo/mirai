"""JSON parsing utilities for LLM responses."""

import json
import re
from typing import Any, Dict


def parse_llm_json_response(content: str) -> Dict[str, Any]:
    """
    Parse JSON from LLM response, handling various formats and invalid characters.
    
    Handles:
    - JSON wrapped in markdown code blocks (```json ... ```)
    - JSON wrapped in plain code blocks (``` ... ```)
    - Raw JSON strings
    - Invalid control characters (newlines, tabs in strings)
    - Trailing commas
    - Comments (removes them)
    
    Args:
        content: Raw LLM response content
    
    Returns:
        Parsed JSON as dictionary
    
    Raises:
        json.JSONDecodeError: If JSON cannot be parsed after all attempts
    """
    # Step 1: Extract JSON from markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        # Try to find JSON block (might be plain code block)
        parts = content.split("```")
        for i in range(1, len(parts), 2):  # Check every other part (code blocks)
            candidate = parts[i].strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()  # Remove "json" prefix
            if candidate.startswith("{") or candidate.startswith("["):
                content = candidate
                break
    
    # Step 2: Remove invalid control characters (but preserve \n in strings as \\n)
    # Replace actual newlines/tabs in JSON with escaped versions
    content = re.sub(r'\n(?=\s*"[^"]*":)', ' ', content)  # Remove newlines before keys
    content = re.sub(r'\n(?=\s*[}\]])', ' ', content)  # Remove newlines before closing braces
    content = re.sub(r'\n(?=\s*[{\[])', ' ', content)  # Remove newlines before opening braces
    
    # Step 3: Remove trailing commas before closing braces/brackets
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # Step 4: Remove single-line comments (// ...)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    
    # Step 5: Try to parse JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # If parsing fails, try to fix common issues
        
        # Try removing control characters more aggressively
        # Replace actual newlines/tabs/carriage returns with spaces (but keep escaped ones)
        fixed_content = ""
        i = 0
        while i < len(content):
            char = content[i]
            # Check if it's an escaped character
            if char == '\\' and i + 1 < len(content):
                next_char = content[i + 1]
                if next_char in ['n', 't', 'r', '\\', '"']:
                    fixed_content += char + next_char
                    i += 2
                    continue
            # Replace actual control characters with spaces
            if ord(char) < 32 and char not in ['\t', '\n', '\r']:
                # Skip invalid control characters
                i += 1
                continue
            elif char in ['\n', '\r', '\t']:
                # Replace with space if not escaped
                fixed_content += ' '
                i += 1
                continue
            fixed_content += char
            i += 1
        
        # Try parsing again
        try:
            return json.loads(fixed_content)
        except json.JSONDecodeError:
            # Last resort: try to extract JSON object/array using regex
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', fixed_content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # If all else fails, raise the original error
            raise e


def safe_parse_llm_json_response(content: str, fallback: Any = None) -> Any:
    """
    Safely parse JSON from LLM response with fallback.
    
    Args:
        content: Raw LLM response content
        fallback: Value to return if parsing fails (default: None)
    
    Returns:
        Parsed JSON or fallback value
    """
    try:
        return parse_llm_json_response(content)
    except Exception as e:
        print(f"   [WARNING] Failed to parse JSON response: {e}")
        if fallback is not None:
            return fallback
        raise


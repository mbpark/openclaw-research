"""Shared API key loader."""
import os

def get_api_key():
    """Load Anthropic API key."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        return api_key
    
    try:
        from pathlib import Path
        from dotenv import load_dotenv
        load_dotenv(Path('..') / '.env')
        return os.environ.get('ANTHROPIC_API_KEY')
    except:
        pass
    
    return None

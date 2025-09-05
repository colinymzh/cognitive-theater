# app/config.py
import os
from dotenv import load_dotenv

def load_api_key(key_name: str) -> str:
    """Load the specified API key"""
    load_dotenv()
    api_key = os.getenv(key_name)
    if not api_key:
        raise ValueError(f"Error: Please set {key_name} in your .env file")
    return api_key

POE_API_KEY = load_api_key("POE_API_KEY")
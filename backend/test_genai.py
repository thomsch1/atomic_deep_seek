#!/usr/bin/env python3
"""
Simple test to verify Google Generative AI is working with the current API.
"""

import os
from dotenv import load_dotenv
from google import genai

def main():
    """Test Gemini API configuration."""
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return 1
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Create GenAI client
        client = genai.Client(api_key=api_key)
        print("✅ GenAI client created successfully")
        
        # Test simple generation
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Say hello world in a friendly way"
        )
        print(f"✅ API call successful: {response.text[:50]}...")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
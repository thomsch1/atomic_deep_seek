#!/usr/bin/env python3
"""
Simple test to verify Google Generative AI is working with the current API.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

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
        # Configure GenAI
        genai.configure(api_key=api_key)
        print("✅ GenAI configured successfully")
        
        # Create a simple model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print(f"✅ Model created: {model}")
        
        # Test simple generation
        response = model.generate_content("Say hello world in a friendly way")
        print(f"✅ API call successful: {response.text[:50]}...")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
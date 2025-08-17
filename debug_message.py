#!/usr/bin/env python3
"""Debug script to isolate the Message validation issue."""

import sys
import os
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src_path)

from agent.state import Message, ResearchState

print("🔍 Testing Message creation...")

# Test basic Message creation
try:
    msg1 = Message(role="user", content="Test message content")
    print("✅ Basic Message creation works")
    print(f"   Message: {msg1}")
    print(f"   Content type: {type(msg1.content)}")
except Exception as e:
    print(f"❌ Basic Message creation failed: {e}")

# Test Message with longer content (similar to error)
try:
    long_content = "Your goal is to generate search queries for the research topic: What is the capital of France?"
    msg2 = Message(role="assistant", content=long_content)
    print("✅ Message with long content works")
    print(f"   Content length: {len(msg2.content)}")
except Exception as e:
    print(f"❌ Message with long content failed: {e}")

# Test ResearchState message addition
try:
    state = ResearchState()
    state.add_message("user", "What is the capital of France?")
    print("✅ ResearchState.add_message works")
    print(f"   Messages count: {len(state.messages)}")
    print(f"   First message: {state.messages[0]}")
except Exception as e:
    print(f"❌ ResearchState.add_message failed: {e}")

# Test model_dump
try:
    state = ResearchState()
    state.add_message("user", "Test")
    state.add_message("assistant", "Response")
    dumped = [msg.model_dump() for msg in state.messages]
    print("✅ Message model_dump works")
    print(f"   Dumped messages: {dumped}")
except Exception as e:
    print(f"❌ Message model_dump failed: {e}")
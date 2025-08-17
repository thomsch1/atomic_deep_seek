#!/usr/bin/env python3
"""
Atomic Agent Research Server
Replaces LangGraph CLI for running the backend server.
"""

import uvicorn
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path for local development
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def main():
    """Run the Atomic Agent research server."""
    parser = argparse.ArgumentParser(description="Run Atomic Agent Research Server")
    parser.add_argument(
        "--host", 
        default=os.getenv("SERVER_HOST", "0.0.0.0"), 
        help="Host to bind to (default from SERVER_HOST env var or 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("SERVER_PORT", "8000")), 
        help="Port to bind to (default from SERVER_PORT env var or 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to environment file (default: .env)"
    )
    
    args = parser.parse_args()
    
    # Load environment file if it exists
    env_file = Path(args.env_file)
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        load_dotenv(env_file)
    else:
        # Try to load default .env file
        load_dotenv()
    
    # Check for required environment variables
    required_env_vars = ["GEMINI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return 1
    
    print(f"Starting Atomic Agent Research Server on {args.host}:{args.port}")
    print("Available endpoints:")
    print(f"  - API: http://{args.host}:{args.port}/research")
    print(f"  - Health: http://{args.host}:{args.port}/health")
    print(f"  - Docs: http://{args.host}:{args.port}/docs")
    print(f"  - Frontend: http://{args.host}:{args.port}/app")
    
    # Run the server
    uvicorn.run(
        "agent.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        env_file=args.env_file if env_file.exists() else None
    )


if __name__ == "__main__":
    exit(main() or 0)
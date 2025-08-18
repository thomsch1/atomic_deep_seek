import argparse
import asyncio
from dotenv import load_dotenv
from agent.orchestrator import ResearchOrchestrator


def main() -> None:
    """Run the research agent from the command line."""
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Run the LangGraph research agent")
    parser.add_argument("question", help="Research question")
    parser.add_argument(
        "--initial-queries",
        type=int,
        default=3,
        help="Number of initial search queries",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=2,
        help="Maximum number of research loops",
    )
    parser.add_argument(
        "--reasoning-model",
        default="gemini-2.5-pro",
        help="Model for the final answer",
    )
    args = parser.parse_args()

    # Create configuration dictionary
    config_dict = {
        "number_of_initial_queries": args.initial_queries,
        "max_research_loops": args.max_loops,
        "answer_model": args.reasoning_model
    }
    
    # Create orchestrator and run research
    orchestrator = ResearchOrchestrator(config_dict)
    result = asyncio.run(orchestrator.run_research_async(args.question))
    
    # Print the result
    print(result)


if __name__ == "__main__":
    main()

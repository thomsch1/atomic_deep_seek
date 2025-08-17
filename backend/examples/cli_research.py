import argparse
from agent.graph import graph
from agent.state import Message


def main() -> None:
    """Run the research agent from the command line."""
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

    state = {
        "messages": [{"role": "user", "content": args.question}],
        "initial_search_query_count": args.initial_queries,
        "max_research_loops": args.max_loops,
        "reasoning_model": args.reasoning_model,
    }

    result = graph.invoke(state)
    
    # Handle the new result format
    if "final_answer" in result:
        print(result["final_answer"])
    else:
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, dict):
                print(last_message.get("content", ""))
            else:
                print(last_message.content)


if __name__ == "__main__":
    main()

"""
Main entry point for the LangGraph code agent.
Usage: python main.py "Add user authentication feature"
"""
import sys
from typing import List
from langchain.schema import HumanMessage
from agent.graph import create_agent_graph
from agent.nodes import AgentState
from dotenv import load_dotenv

def main(feature_request: str):
    """Run the agent with the given feature request."""
    # Load environment variables
    load_dotenv()
    
    # Create the agent graph
    agent = create_agent_graph()
    
    # Initialize state
    initial_state = AgentState(
        feature_request=feature_request,
        project_config={},
        plan=[],
        code_changes=[],
        test_results="",
        branch_name="",
        messages=[HumanMessage(content=f"Feature request: {feature_request}")]
    )
    
    # Run the agent
    print(f"🚀 Starting agent for: {feature_request}")
    print("-" * 50)
    
    # Execute the graph
    # Reference: https://langchain-ai.github.io/langgraph/how-tos/streaming-tokens/
    for event in agent.stream(initial_state):
        for node, state in event.items():
            print(f"✓ Completed: {node}")
            if state.get("messages"):
                print(f"  → {state['messages'][-1].content}")
    
    print("-" * 50)
    print("✅ Agent workflow complete!")
    print(f"📄 Review document created: REVIEW-{state.get('branch_name', 'unknown')}.md")
    print(f"🌿 Branch created: {state.get('branch_name', 'unknown')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<feature request>\"")
        sys.exit(1)
    
    feature_request = sys.argv[1]
    main(feature_request)
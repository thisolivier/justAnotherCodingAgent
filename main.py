"""
Main entry point for the LangGraph code agent.
Usage: python main.py --project /path/to/project "Add user authentication feature"
"""
import sys
import os
import argparse
from pathlib import Path
from os import PathLike
from typing import Union
from langchain.schema import HumanMessage
from agent.graph import create_agent_graph
from agent.nodes import AgentState
from dotenv import load_dotenv

PathType = Union[str, PathLike[str]]

def main(feature_request: str, project_path: PathType):
    """Run the agent with the given feature request on the specified project."""
    # Load environment variables
    load_dotenv()
    
    # Validate project path
    project_path = Path(project_path).resolve()
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    config_path = project_path / "config.yaml"
    if not config_path.exists():
        print(f"❌ Error: No config.yaml found in project: {project_path}")
        print("  Please create a config.yaml file in your project root")
        sys.exit(1)
    
    # Create the agent graph with project context
    agent = create_agent_graph(project_path)
    
    # Initialize state with project path
    initial_state = AgentState(
        feature_request=feature_request,
        project_path=str(project_path),  # Add project path to state
        project_config={},
        plan=[],
        code_changes=[],
        test_results="",
        branch_name="",
        messages=[HumanMessage(content=f"Feature request: {feature_request}")]
    )
    
    print(f"🚀 Starting agent for: {feature_request}")
    print(f"📁 Working on project: {project_path}")
    print("-" * 50)
    
    # Execute the graph
    for event in agent.stream(initial_state):
        for node, state in event.items():
            print(f"✓ Completed: {node}")
            if state.get("messages"):
                print(f"  → {state['messages'][-1].content}")
    
    print("-" * 50)
    print("✅ Agent workflow complete!")
    print(f"📄 Review document created: {project_path}/REVIEW-{state.get('branch_name', 'unknown')}.md")
    print(f"🌿 Branch created: {state.get('branch_name', 'unknown')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangGraph Code Agent")
    parser.add_argument("feature_request", help="Natural language feature request")
    parser.add_argument("--project", "-p", required=True, help="Path to target project")
    
    args = parser.parse_args()
    main(args.feature_request, args.project)
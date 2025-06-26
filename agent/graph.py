"""Main LangGraph workflow definition with project awareness."""
from langgraph.graph import StateGraph, END
from pathlib import Path
from agent.nodes import (
    AgentState,
    load_config_node,
    plan_node,
    generate_code_node,
    run_tests_node,
    create_review_doc_node
)
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

def create_agent_graph(project_path: Path):
    """
    Create the LangGraph workflow for the coding agent.
    
    Args:
        project_path: Path to the target project
    """
    
    # Initialize LLM based on environment variable
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    if llm_provider == "openai":
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    else:
        llm = ChatAnthropic(model="claude-opus-4-20250514", temperature=0.3)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes with project context
    workflow.add_node("load_config", load_config_node)
    workflow.add_node("plan", lambda state: plan_node(state, llm))
    workflow.add_node("generate_code", lambda state: generate_code_node(state, llm, project_path))
    workflow.add_node("run_tests", lambda state: run_tests_node(state, project_path))
    workflow.add_node("create_review_doc", lambda state: create_review_doc_node(state, project_path))
    
    # Define the edges (flow)
    workflow.set_entry_point("load_config")
    workflow.add_edge("load_config", "plan")
    workflow.add_edge("plan", "generate_code")
    workflow.add_edge("generate_code", "run_tests")
    workflow.add_edge("run_tests", "create_review_doc")
    workflow.add_edge("create_review_doc", END)
    
    # Compile the graph
    return workflow.compile()
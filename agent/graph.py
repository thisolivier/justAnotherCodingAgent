"""
Main LangGraph workflow definition.
This ties together all the nodes into a cohesive workflow.
Reference: https://langchain-ai.github.io/langgraph/tutorials/introduction/
"""
from langgraph.graph import StateGraph, END
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

def create_agent_graph():
    """
    Create the LangGraph workflow for the coding agent.
    
    The graph follows this flow:
    1. Load Config -> 2. Plan -> 3. Generate Code -> 4. Run Tests -> 5. Create Review Doc
    """
    
    # Initialize LLM based on environment variable
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    if llm_provider == "openai":
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    else:
        llm = ChatAnthropic(model="claude-opus-4-20250514", temperature=0.3)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("load_config", load_config_node)
    workflow.add_node("plan", lambda state: plan_node(state, llm))
    workflow.add_node("generate_code", lambda state: generate_code_node(state, llm))
    workflow.add_node("run_tests", run_tests_node)
    workflow.add_node("create_review_doc", create_review_doc_node)
    
    # Define the edges (flow)
    workflow.set_entry_point("load_config")
    workflow.add_edge("load_config", "plan")
    workflow.add_edge("plan", "generate_code")
    workflow.add_edge("generate_code", "run_tests")
    workflow.add_edge("run_tests", "create_review_doc")
    workflow.add_edge("create_review_doc", END)
    
    # Compile the graph
    return workflow.compile()
"""
Node implementations for the LangGraph workflow.
Each node represents a step in the agent's workflow.
Reference: https://langchain-ai.github.io/langgraph/tutorials/introduction/
"""
from langchain.schema import HumanMessage
from agent.config import load_project_config
import json
from datetime import datetime
from pathlib import Path
from ..lib import Context, AgentState

def load_config_node(state: AgentState, context: Context) -> AgentState:
    """Load project configuration from YAML/JSON file."""
    project_path = Path(context.project_path)
    config_path = project_path / "config.yaml"
    
    config = load_project_config(str(config_path))
    state.project_config = config
    state.messages.append(
        HumanMessage(content=f"Loaded project config: {config['project']['name']} from {project_path}")
    )
    return state

def plan_node(state: AgentState, llm) -> AgentState:
    """
    Plan the implementation steps based on the feature request.
    The LLM analyzes the request and creates a step-by-step plan.
    """
    prompt = f"""
    Given the following feature request and project configuration, create an implementation plan.
    
    Feature Request: {state.feature_request}
    
    Project Config:
    {json.dumps(state.project_config, indent=2)}
    
    Create a numbered list of specific implementation steps. Be concrete and actionable.
    Consider the project's file structure, coding standards, and testing requirements.
    Consider whether the level of detail required for the requested feature.
    """
    
    response = llm.invoke(prompt)
    
    # Parse the plan from LLM response
    plan_text = response.content if hasattr(response, 'content') else str(response)
    steps = [step.strip() for step in plan_text.split('\n') if step.strip() and any(char.isdigit() for char in step[:3])]
    
    state.plan = steps
    state.messages.append(HumanMessage(content=f"Created plan with {len(steps)} steps"))
    return state

def run_tests_node(state: AgentState, context: Context) -> AgentState:
    """Run project tests using the configured test command."""
    run_tool = context.tools["run_command"]
    
    test_command = state.project_config["testing"]["command"]
    result = run_tool.run({"command": test_command})
    
    state.test_results = result
    state.messages.append(HumanMessage(content="Ran tests"))
    return state

def create_review_doc_node(state: AgentState, context: Context) -> AgentState:
    """Create the review documentation for the feature."""
    
    # Generate branch name
    feature_name = state.feature_request[:30].lower().replace(" ", "-")
    branch_prefix = state.project_config["git"]["branch_prefix"]
    state.branch_name = f"{branch_prefix}{feature_name}-{datetime.now().strftime('%Y%m%d')}"
    
    # Create review document
    review_content = f"""# Feature: {state.feature_request}

    ## Summary
    Implementation of requested feature based on the provided requirements.

    ## Changes Made
    """
        
    for change in state.code_changes:
        review_content += f"- {change['action']} `{change['file']}`\n"
        
    review_content += f"""
    ## Implementation Plan
    """
    for i, step in enumerate(state.plan, 1):
        review_content += f"{i}. {step}\n"
    
    review_content += f"""
    ## Testing
    - Test command: `{state.project_config["testing"]["command"]}`
    - Results: {state.test_results}
    ## Review Checklist
    - [ ] Code follows project style guidelines
    - [ ] Tests pass
    - [ ] Documentation updated
    - [ ] No sensitive data exposed

    ## Next Steps
    Please review the changes and provide feedback.
    """
    
    # Write review document
    write_tool = context.tools["write_file"]
    review_file = f"REVIEW-{state.branch_name}.md"
    write_tool.run({"file_path": review_file, "content": review_content})
    
    # Checkout new branch
    git_tool = context.tools["git_checkout"]
    git_tool.run({"branch_name": state.branch_name})
    
    state.messages.append(HumanMessage(content=f"Created review doc and branch: {state.branch_name}"))
    return state
"""
Node implementations for the LangGraph workflow.
Each node represents a step in the agent's workflow.
Reference: https://langchain-ai.github.io/langgraph/tutorials/introduction/
"""
from typing import Dict, Any, List, Optional
from langchain.schema import BaseMessage, HumanMessage
from agent.tools import get_tools
from agent.config import load_project_config
import json
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from agent.lib.context import Context

class AgentState(BaseModel):
    feature_request: str
    project_path: Path
    project_config: Dict[str, Any] = Field(default_factory=dict)
    plan: List[str] = Field(default_factory=list)
    code_changes: List[Dict[str, str]] = Field(default_factory=list)
    test_results: Optional[str] = None
    branch_name: Optional[str] = None
    messages: List[BaseMessage] = Field(default_factory=list)

def load_config_node(state: AgentState) -> AgentState:
    """Load project configuration from YAML/JSON file."""
    project_path = Path(state.project_path)
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

def generate_code_node(state: AgentState, context: Context, llm) -> AgentState:
    """
    Generate or modify code based on the plan.
    This node uses tools to read existing files and write new ones.
    """
    code_changes = []
    
    # For each step in the plan, determine if code needs to be generated
    for step in state.plan[:3]:  # Limit to first 3 steps for MVP
        prompt = f"""
        Implement the following step from the plan:
        {step}
        
        Project language: {state.project_config['project']['language']}
        Code style: {json.dumps(state.project_config.get('code_style', {}), indent=2)}
        
        If this step requires code changes:
        1. Specify the file path
        2. Provide the complete file content
        3. Follow the project's coding standards
        
        Format your response as:
        FILE_PATH: <path>
        CONTENT:
        <file content>
        """
        
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Simple parsing - in production, use more robust parsing
        if "FILE_PATH:" in content and "CONTENT:" in content:
            parts = content.split("CONTENT:")
            file_path = parts[0].replace("FILE_PATH:", "").strip()
            file_content = parts[1].strip()
            
            # Use write tool
            write_tool = context.tools["write_file"]
            result = write_tool.run({"file_path": file_path, "content": file_content})
            
            code_changes.append({
                "file": file_path,
                "action": "created/modified",
                "result": result
            })
    
    state.code_changes = code_changes
    state.messages.append(HumanMessage(content=f"Generated {len(code_changes)} code changes"))
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

from langchain.schema import HumanMessage
from ..lib import Context, AgentState
import json

# TODO: Import AgentState
# TODO: Modularise nodes (own directory)

def _normalise_implementation_steps(state):
    """
    Return up to the first 3 plan steps if available,
    otherwise fall back to using the single feature request.
    """
    if state.plan and len(state.plan) > 0:
        return state.plan[:3]
    # Fallback: treat the feature request itself as the one step to implement
    return [state.feature_request]


def _generate_for_step(step, state, context, llm):
    """
    Generate or modify code based on a single step using the LLM.
    Returns a list of code change records.
    """
    prompt = f"""
    You are a software engineer. Implement the following step:
    {step}

    Project language: {state.project_config['project']['language']}
    Code style: {json.dumps(state.project_config.get('code_style', {}), indent=2)}

    If this step requires code changes, then for each file:
    1. Specify the file path
    2. Provide the complete file content
    3. Follow the project's coding standards

    The content provided should be raw text with no decorators such as: ``` javascript
    More than one file can be included in each response.

    Format your response as:
    _FILE_PATH: <path>
    _CONTENT:
    <file content>
    """
    response = llm.invoke(prompt)
    content = getattr(response, 'content', str(response))
    changes = []
    #split content by FilePath
    #for each chunk
      #split by content
      #take the chunk before, it's the file path
      #take the chunk after, it's the content
    
    if '_FILE_PATH:' in content:
        files = content.split('_FILE_PATH:')
        for file in files:
            if '_CONTENT:' in file:        
              file_path, rest = file.split('_CONTENT:', 1)
              file_path = file_path.strip()
              file_content = rest.strip()
              print("==============")
              print("Path:", file_path)
              print("Content:\n", file_content)
              write_tool = context.tools['write_file']
              result = write_tool.run({
                  'file_path': file_path,
                  'content': file_content
              })

              changes.append({
                  'file': file_path,
                  'action': 'created/modified',
                  'result': result
              })
    return changes


def generate_code_node(state: AgentState, context: Context, llm) -> AgentState:
    """
    Generate or modify code based on either planned steps (if present)
    or directly from the feature request.
    """
    code_changes = []
    steps = _normalise_implementation_steps(state)

    for step in steps:
        code_changes.extend(_generate_for_step(step, state, context, llm))

    state.code_changes = code_changes
    state.messages.append(HumanMessage(
        content=f"Generated {len(code_changes)} code changes"
    ))
    return state

import json
from agent.lib import AgentState
from agent.graph import create_agent_graph
from pathlib import Path


# 1. Compile
graph = create_agent_graph(Path('./dummyCodebase'))

# 2. Prepare input state
state = AgentState(
  feature_request="", 
  project_config={}, 
  file_manifest=[], 
  symbol_index={}, 
  plan=[], 
  code_changes=[], 
  messages=[]
  )

# 3. Invoke only the "agent" node
output = graph.nodes["boostrap_codebase"].invoke(state)
print(json.dumps(output, indent=2))

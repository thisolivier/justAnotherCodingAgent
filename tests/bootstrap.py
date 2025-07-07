import json
from agent.lib import AgentState
from agent.graph import create_agent_graph
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# 1. Compile
graph = create_agent_graph(Path('./tests/dummyCodebase'))

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
print(f"🚀 Starting test of boostrap_codebase node")
output = graph.nodes["bootstrap_codebase"].invoke(state)
print(output)

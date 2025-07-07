from typing import Dict, Any, List, Optional
from langchain.schema import BaseMessage
from pathlib import Path
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    feature_request: str
    project_config: Dict[str, Any] = Field(default_factory=dict)
    file_manifest: List[str] = Field(default_factory=list)
    symbol_index: Dict[str, list[str]] = Field(default_factory=dict)
    plan: List[str] = Field(default_factory=list)
    code_changes: List[Dict[str, str]] = Field(default_factory=list)
    test_results: Optional[str] = None
    branch_name: Optional[str] = None
    messages: List[BaseMessage] = Field(default_factory=list)
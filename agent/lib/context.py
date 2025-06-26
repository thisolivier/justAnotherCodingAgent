from typing import Any
from dataclasses import dataclass
from agent.tools import ProjectAwareTool
from pathlib import Path

@dataclass(frozen=True)
class Context:
    project_path: Path
    llm: Any
    tools: dict[str, ProjectAwareTool]
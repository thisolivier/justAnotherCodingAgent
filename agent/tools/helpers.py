from pathlib import Path
from langchain.tools import BaseTool

def sanitize_path(project_root: Path, relative_path: str) -> Path:
    """
    Resolve a relative path against project_root and ensure no path traversal occurs.
    """
    full_path = (project_root / relative_path).resolve()
    if project_root.resolve() not in full_path.parents and full_path != project_root.resolve():
        raise ValueError("Invalid path: outside project directory")
    return full_path


class ProjectAwareTool(BaseTool):
    """Base class for tools that need project context and async support."""
    project_path: Path = Path("")

    def set_project_path(self, project_path: Path):
        self.project_path = project_path.resolve()
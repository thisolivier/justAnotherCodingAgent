from typing import List
from pathlib import Path
from .helpers import ProjectAwareTool

from .miskTools import RunCommandTool, GitCheckoutTool
from .readFileTool import ReadFileTool
from .fileEnumerateTool import FileEnumerateTool
from .writeFileTool import WriteFileTool

def get_tools(project_path: Path) -> List[ProjectAwareTool]:
    """Get instantiated tools configured for specific project path."""
    raw = [ReadFileTool, WriteFileTool, RunCommandTool, GitCheckoutTool, FileEnumerateTool]
    instances: List[ProjectAwareTool] = []
    for ToolClass in raw:
        inst = ToolClass()
        inst.set_project_path(project_path)
        instances.append(inst)
    return instances

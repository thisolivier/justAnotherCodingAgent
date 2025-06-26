import os
import subprocess
import asyncio
from typing import Dict, Any, Optional, List, Type
from pathlib import Path
import git
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


def _sanitize_path(project_root: Path, relative_path: str) -> Path:
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


class ReadFileInput(BaseModel):
    file_path: str = Field(description="Path to the file to read (relative to project root)")


class ReadFileTool(ProjectAwareTool):
    name: str = "read_file"
    description: str = "Read contents of a file relative to project root"
    args_schema: Type[ReadFileInput] = ReadFileInput

    def _run(self, file_path: str) -> str:
        try:
            full_path = _sanitize_path(self.project_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except ValueError:
            return "Error reading file: invalid file path"
        except Exception:
            return "Error reading file"

    async def _arun(self, file_path: str) -> str:
        return await asyncio.to_thread(self._run, file_path)


class WriteFileInput(BaseModel):
    file_path: str = Field(description="Path to write (relative to project root)")
    content: str = Field(description="Content to write to the file")


class WriteFileTool(ProjectAwareTool):
    name: str = "write_file"
    description: str = "Write content to a file relative to project root"
    args_schema: Type[WriteFileInput] = WriteFileInput

    def _run(self, file_path: str, content: str) -> str:
        try:
            full_path = _sanitize_path(self.project_path, file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except ValueError:
            return "Error writing file: invalid file path"
        except Exception:
            return "Error writing file"

    async def _arun(self, file_path: str, content: str) -> str:
        return await asyncio.to_thread(self._run, file_path, content)


class RunCommandInput(BaseModel):
    command: str = Field(description="Shell command to execute (e.g., 'npm test', 'ls -la')")
    cwd: Optional[str] = Field(
        default=None,
        description="Working directory relative to project root (e.g., 'src', 'tests')"
    )


class RunCommandTool(ProjectAwareTool):
    name: str = "run_command"
    description: str = "Run a shell command in the project directory"
    args_schema: Type[RunCommandInput] = RunCommandInput

    def _run(self, command: str, cwd: Optional[str] = None) -> str:
        try:
            working_dir = self.project_path
            if cwd:
                working_dir = _sanitize_path(self.project_path, cwd)

            result = subprocess.run(
                command,
                shell=True,
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            return (
                f"Exit code: {result.returncode}\n"
                f"Output:\n{result.stdout}\n"
                f"Errors:\n{result.stderr}"
            )
        except ValueError:
            return "Error running command: invalid working directory"
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception:
            return "Error running command"

    async def _arun(self, command: str, cwd: Optional[str] = None) -> str:
        return await asyncio.to_thread(self._run, command, cwd)


class GitCheckoutInput(BaseModel):
    branch_name: str = Field(
        description="Name of the branch to create and checkout (e.g., 'feature/add-auth', 'fix/bug-123')"
    )


class GitCheckoutTool(ProjectAwareTool):
    name: str = "git_checkout"
    description: str = "Create and checkout a new git branch in the project"
    args_schema: Type[GitCheckoutInput] = GitCheckoutInput

    def _run(self, branch_name: str) -> str:
        try:
            repo = git.Repo(str(self.project_path))
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            return f"Successfully created and checked out branch: {branch_name}"
        except Exception:
            return "Error with git operation"

    async def _arun(self, branch_name: str) -> str:
        return await asyncio.to_thread(self._run, branch_name)


def get_tools(project_path: Path) -> List[ProjectAwareTool]:
    """Get instantiated tools configured for specific project path."""
    raw = [ReadFileTool, WriteFileTool, RunCommandTool, GitCheckoutTool]
    instances: List[ProjectAwareTool] = []
    for ToolClass in raw:
        inst = ToolClass()
        inst.set_project_path(project_path)
        instances.append(inst)
    return instances

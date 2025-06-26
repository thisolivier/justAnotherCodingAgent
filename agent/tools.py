"""
Tools for the LangGraph agent to interact with the filesystem and git.
Reference: https://python.langchain.com/docs/modules/agents/tools/custom_tools
"""
import os
import subprocess
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List
import git
from pathlib import Path

class ProjectAwareTool(BaseTool):
    """Base class for tools that need project context."""
    project_path: Path = Path("")
    
    def set_project_path(self, project_path: Path):
        self.project_path = project_path

class ReadFileInput(BaseModel):
    file_path: str = Field(description="Path to the file to read (relative to project root)")

class ReadFileTool(ProjectAwareTool):
    name = "read_file"
    description = "Read contents of a file relative to project root"
    args_schema = ReadFileInput
    
    def _run(self, file_path: str) -> str:
        """Read file contents relative to project path."""
        try:
            full_path = self.project_path / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WriteFileInput(BaseModel):
    file_path: str = Field(description="Path to write (relative to project root)")
    content: str = Field(description="Content to write to the file")

class WriteFileTool(ProjectAwareTool):
    name = "write_file"
    description = "Write content to a file relative to project root"
    args_schema = WriteFileInput
    
    def _run(self, file_path: str, content: str) -> str:
        """Write content to file relative to project path."""
        try:
            full_path = self.project_path / file_path
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

# Define the input schema
class RunCommandInput(BaseModel):
    command: str = Field(
        description="Shell command to execute (e.g., 'npm test', 'ls -la')"
    )
    cwd: Optional[str] = Field(
        default=None, 
        description="Working directory relative to project root (e.g., 'src', 'tests')"
    )

class RunCommandTool(ProjectAwareTool):
    name = "run_command"
    description = "Run a shell command in the project directory"
    args_schema = RunCommandInput
    
    def _run(self, command: str, cwd: Optional[str] = None) -> str:
        """Run command in project directory."""
        try:
            # Use project path as working directory
            working_dir = self.project_path
            if cwd:
                working_dir = self.project_path / cwd
                
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            return f"Exit code: {result.returncode}\nOutput:\n{result.stdout}\nErrors:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error running command: {str(e)}"
        
class GitCheckoutInput(BaseModel):
    branch_name: str = Field(
        description="Name of the branch to create and checkout (e.g., 'feature/add-auth', 'fix/bug-123')"
    )

class GitCheckoutTool(ProjectAwareTool):
    name = "git_checkout"
    description = "Create and checkout a new git branch in the project"
    args_schema = GitCheckoutInput
    
    def _run(self, branch_name: str) -> str:
        """Create and checkout a new branch in project repo."""
        try:
            repo = git.Repo(str(self.project_path))
            # Create new branch from current HEAD
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            return f"Successfully created and checked out branch: {branch_name}"
        except Exception as e:
            return f"Error with git operation: {str(e)}"

# Updated get_tools function
def get_tools(project_path: Path) -> List[BaseTool]:
    """Get tools configured for specific project path."""
    tools = [
        ReadFileTool,
        WriteFileTool,
        RunCommandTool,
        GitCheckoutTool
    ]
    
    # Set project path for all tools
    for tool in tools:
        if isinstance(tool, ProjectAwareTool):
            tool.set_project_path(project_path)
    
    return tools
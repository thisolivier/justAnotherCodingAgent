"""
Tools for the LangGraph agent to interact with the filesystem and git.
Reference: https://python.langchain.com/docs/modules/agents/tools/custom_tools
"""
import os
import subprocess
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import git

class ReadFileInput(BaseModel):
    file_path: str = Field(description="Path to the file to read")

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read contents of a file"
    args_schema = ReadFileInput
    
    def _run(self, file_path: str) -> str:
        """Read file contents safely."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WriteFileInput(BaseModel):
    file_path: str = Field(description="Path to the file to write")
    content: str = Field(description="Content to write to the file")

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file"
    args_schema = WriteFileInput
    
    def _run(self, file_path: str, content: str) -> str:
        """Write content to file safely."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class RunCommandInput(BaseModel):
    command: str = Field(description="Command to run")
    cwd: Optional[str] = Field(default=None, description="Working directory")

class RunCommandTool(BaseTool):
    name = "run_command"
    description = "Run a shell command"
    args_schema = RunCommandInput
    
    def _run(self, command: str, cwd: Optional[str] = None) -> str:
        """Run command and capture output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
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
    branch_name: str = Field(description="Name of the branch to create/checkout")

class GitCheckoutTool(BaseTool):
    name = "git_checkout"
    description = "Create and checkout a new git branch"
    args_schema = GitCheckoutInput
    
    def _run(self, branch_name: str) -> str:
        """Create and checkout a new branch."""
        try:
            repo = git.Repo('.')
            # Create new branch from current HEAD
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            return f"Successfully created and checked out branch: {branch_name}"
        except Exception as e:
            return f"Error with git operation: {str(e)}"

# Initialize tools
def get_tools():
    return [
        ReadFileTool, # Note: Removed parens
        WriteFileTool,
        RunCommandTool,
        GitCheckoutTool
    ]
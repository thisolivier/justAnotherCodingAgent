import subprocess
import asyncio
from typing import Optional, Type
import git
from pydantic import BaseModel, Field
from .helpers import sanitize_path, ProjectAwareTool


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
                working_dir = sanitize_path(self.project_path, cwd)

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
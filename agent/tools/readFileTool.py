import asyncio
from typing import Type
from pydantic import BaseModel, Field
from .helpers import sanitize_path, ProjectAwareTool

class ReadFileInput(BaseModel):
    file_path: str = Field(description="Path to the file to read (relative to project root)")


class ReadFileTool(ProjectAwareTool):
    name: str = "read_file"
    description: str = "Read contents of a file relative to project root"
    args_schema: Type[ReadFileInput] = ReadFileInput

    def _run(self, file_path: str) -> str:
        try:
            full_path = sanitize_path(self.project_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except ValueError:
            return "Error reading file: invalid file path"
        except Exception:
            return "Error reading file"

    async def _arun(self, file_path: str) -> str:
        return await asyncio.to_thread(self._run, file_path)
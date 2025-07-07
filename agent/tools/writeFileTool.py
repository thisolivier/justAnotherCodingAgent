import asyncio
from typing import Type
from pydantic import BaseModel, Field
from .helpers import sanitize_path, ProjectAwareTool

class WriteFileInput(BaseModel):
    file_path: str = Field(description="Path to write (relative to project root)")
    content: str = Field(description="Content to write to the file")


class WriteFileTool(ProjectAwareTool):
    name: str = "write_file"
    description: str = "Write content to a file relative to project root"
    args_schema = WriteFileInput

    def _run(self, file_path: str, content: str) -> str:
        try:
            full_path = sanitize_path(self.project_path, file_path)
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
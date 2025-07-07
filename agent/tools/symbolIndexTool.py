from .helpers import ProjectAwareTool
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Type
import subprocess
import json

class SymbolIndexInput(BaseModel):
    file_paths: list[str] = Field(
        ..., description="List of file paths (relative or absolute) to index symbols from"
    )

class SymbolIndexTool(ProjectAwareTool):
    name: str = "symbol_index"
    description: str = (
        "Generate an index of language symbols in specified files. "
        "Uses universal-ctags on the provided file list and returns a dict mapping "
        "file paths to lists of symbol objects (name, kind, line)."
    )
    args_schema: Type[SymbolIndexInput] = SymbolIndexInput

    def _run(self, file_paths: list[str]) -> dict[str, list[dict]]:
        try:
            # Resolve file paths to absolute if relative provided
            absolute_paths = []
            for path_str in file_paths:
                abs_path = Path(path_str)
                if not abs_path.is_absolute():
                    abs_path = (self.project_path / path_str).resolve()
                if abs_path.is_file():
                    absolute_paths.append(str(abs_path))

            if not absolute_paths:
                return {}

            # Build ctags command for specified files
            cmd = [
                "ctags",
                "--fields=+Ktn",
                "--output-format=json",
                "-f", "-"
            ] + absolute_paths

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            index: dict[str, list[dict]] = {}
            for line in result.stdout.splitlines():
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                file_path = entry.get('path')
                symbol = {
                    'name': entry.get('name'),
                    'kind': entry.get('kind'),
                    'line': entry.get('line')
                }
                index.setdefault(file_path, []).append(symbol)

            return index
        except subprocess.CalledProcessError:
            return {}
        except Exception:
            return {}

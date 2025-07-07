from .helpers import ProjectAwareTool
from pydantic import BaseModel, Field
import subprocess

class DiffManifestInput(BaseModel):
    file_manifest: list[str] = Field(
        ..., description="Existing list of relative file paths"
    )

class DiffManifestTool(ProjectAwareTool):
    name: str = "diff_manifest"
    description: str = (
        "Update the file manifest based on git diffs. "
        "Returns the updated manifest and list of files to re-index (added or modified)."
    )
    args_schema = DiffManifestInput

    def _run(self, file_manifest: list[str]) -> dict:
        try:
            project_root = self.project_path
            # Get git status diffs: added (A), modified (M), deleted (D), untracked (??)
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(project_root), check=True,
                capture_output=True, text=True
            )
            added: list[str] = []
            modified: list[str] = []
            removed: list[str] = []

            for line in result.stdout.splitlines():
                status, path = line[:2].strip(), line[3:]
                if status == 'A' or status == '??':
                    added.append(path)
                elif status == 'M':
                    modified.append(path)
                elif status == 'D':
                    removed.append(path)

            old_set = set(file_manifest)
            new_set = (old_set | set(added)) - set(removed)
            new_manifest = list(new_set)

            # Files to re-index: newly added and modified
            files_to_reindex = list(set(added + modified))

            return {
                "file_manifest": new_manifest,
                "files_to_reindex": files_to_reindex
            }
        except Exception:
            return {
                "file_manifest": file_manifest,
                "files_to_reindex": []
            }

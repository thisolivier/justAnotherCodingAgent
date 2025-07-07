from pathlib import Path
import os
import fnmatch
from .helpers import ProjectAwareTool

class FileEnumerateTool(ProjectAwareTool):
    name: str = "file_enumerate"
    description: str = (
        "Enumerate all files in the project root, skipping patterns defined in .gitignore. "
        "Returns list of relative file paths."
    )

    def _run(self) -> list[str]:
        try:
            project_root = self.project_path
            if not project_root.exists():
                raise FileNotFoundError(f"No such path: {project_root!r}")
            if not project_root.is_dir():
                raise NotADirectoryError(f"Not a directory: {project_root!r}")

            # Load ignore patterns from .gitignore
            gitignore_path = project_root / ".gitignore"
            patterns_to_skip: list[str] = []
            if gitignore_path.is_file():
                for line in gitignore_path.read_text(encoding='utf-8').splitlines():
                    strippedLine = line.strip()
                    if not strippedLine or strippedLine.startswith('#'):
                        continue
                    patterns_to_skip.append(strippedLine)

            print("Preparing to add paths")
            file_paths: list[str] = []
            for root_fs, dirs, files in os.walk(project_root):
                print("Doing a thing...", dirs, files)
                root_path = Path(root_fs)
                relative_root = root_path.relative_to(project_root)
                relative_root_str = str(relative_root).replace("\\", "/")

                # Skip ignored directories
                dirs[:] = [dir for dir in dirs
                           if not any(
                               fnmatch.fnmatch(
                                   f"{relative_root_str}/{dir}" if relative_root_str else dir,
                                   pat.rstrip('/')
                               )
                               for pat in patterns_to_skip
                           )]

                for file_location in files:
                    relative_file_location = (
                        f"{relative_root_str}/{file_location}" if relative_root_str else file_location
                    )
                    if any(fnmatch.fnmatch(relative_file_location, pat) for pat in patterns_to_skip):
                        continue
                    file_paths.append(relative_file_location)

            return file_paths
        except Exception:
            return []

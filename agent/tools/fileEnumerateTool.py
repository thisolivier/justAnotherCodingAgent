from pathlib import Path
import fnmatch
from .helpers import ProjectAwareTool

class FileEnumerateTool(ProjectAwareTool):
    name: str = "file_enumerate"
    description: str = (
        "Enumerate all files in the project root, skipping patterns defined in .gitignore. "
        "Returns list of relative file paths."
    )

    def _run(self) -> list[str]:
        project_root = Path(self.project_path)

        # 1) Fail loudly if the path isn’t right
        if not project_root.exists():
            raise FileNotFoundError(f"No such path: {project_root!r}")
        if not project_root.is_dir():
            raise NotADirectoryError(f"Not a directory: {project_root!r}")

        # 2) (Optional) load your .gitignore patterns here
        gitignore = project_root / ".gitignore"
        patterns = []
        if gitignore.is_file():
          patterns = [l.strip() for l in gitignore.read_text().splitlines()
            if l.strip() and not l.startswith("#")]

        # 3) Walk with pathlib.rglob (simpler than os.walk + Path conversions)
        all_files: list[str] = []
        for path in project_root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(project_root)
            rel_str = str(rel).replace("\\", "/")

            # 4) (Optional) skip based on patterns
            if any(fnmatch.fnmatch(rel_str, pat) for pat in patterns):
               print(f"[DEBUG] skipping {rel_str} because of .gitignore")
               continue

            all_files.append(rel_str)

        print(f"[DEBUG] FileEnumerateTool found {len(all_files)} files.")
        return all_files
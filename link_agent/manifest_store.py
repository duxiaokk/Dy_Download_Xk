from __future__ import annotations

import json
from pathlib import Path


class ManifestStore:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.manifest_path = self.output_dir / "processed_files.json"

    def load(self) -> dict:
        if not self.manifest_path.exists():
            return {}

        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def save(self, manifest: dict) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def get_signature(file_path: Path) -> dict:
        stat = file_path.stat()
        return {
            "path": str(file_path.resolve()),
            "name": file_path.name,
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        }

    @staticmethod
    def is_processed(signature: dict, manifest: dict) -> bool:
        previous = manifest.get(signature["path"])
        if not previous:
            return False

        return (
            previous.get("size") == signature["size"]
            and previous.get("mtime_ns") == signature["mtime_ns"]
        )

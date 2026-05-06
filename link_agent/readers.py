from __future__ import annotations

import csv
from pathlib import Path


class FileReader:
    def read(self, file_path: str | Path) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()
        if suffix == ".txt":
            return self._read_txt(path)
        if suffix == ".csv":
            return self._read_csv(path)

        raise ValueError(f"Unsupported file type: {path}")

    def _read_txt(self, path: Path) -> str:
        for encoding in ("utf-8-sig", "utf-8", "gbk"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Unable to detect text encoding: {path}")

    def _read_csv(self, path: Path) -> str:
        for encoding in ("utf-8-sig", "utf-8", "gbk"):
            try:
                rows_text: list[str] = []

                with path.open("r", encoding=encoding, newline="") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        rows_text.append(" ".join(row))

                return "\n".join(rows_text)
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Unable to detect CSV encoding: {path}")

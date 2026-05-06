from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import LinkRecord


class Writer:
    def save_cleaned_csv(self, records: list[LinkRecord], file_path: str | Path) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["index", "url", "source_file", "is_douyin", "batch_no", "status"],
            )
            writer.writeheader()
            for record in records:
                writer.writerow(asdict(record))

    def save_summary(
        self,
        records: list[LinkRecord],
        output_file: str | Path,
        processed_files: list[dict],
        skipped_files: list[str],
        failed_files: list[dict],
        new_records: list[LinkRecord],
        batch_size: int,
    ) -> None:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        summary = {
            "total_links": len(records),
            "new_links_added_this_run": len(new_records),
            "total_douyin": sum(1 for record in records if record.is_douyin),
            "total_non_douyin": sum(1 for record in records if not record.is_douyin),
            "batch_size": batch_size,
            "total_batches": max((record.batch_no for record in records), default=0),
            "processed_files_this_run": processed_files,
            "skipped_files_this_run": skipped_files,
            "failed_files_this_run": failed_files,
        }

        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_batches(self, records: list[LinkRecord], batch_dir: str | Path) -> None:
        path = Path(batch_dir)
        path.mkdir(parents=True, exist_ok=True)

        for old_file in path.glob("batch_*.txt"):
            old_file.unlink()

        grouped: dict[int, list[LinkRecord]] = {}
        for record in records:
            grouped.setdefault(record.batch_no, []).append(record)

        for batch_no, batch_records in grouped.items():
            batch_file = path / f"batch_{batch_no:03d}.txt"
            batch_file.write_text(
                "\n".join(record.url for record in batch_records),
                encoding="utf-8",
            )

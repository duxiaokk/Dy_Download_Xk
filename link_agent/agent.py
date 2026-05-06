from __future__ import annotations

import shutil
from pathlib import Path

from .config import DEFAULT_OUTPUT_DIR, SUPPORTED_EXTENSIONS
from .link_processor import LinkProcessor
from .manifest_store import ManifestStore
from .models import LinkRecord
from .readers import FileReader
from .writers import Writer


class LinkAgent:
    def __init__(self, batch_size: int = 20, only_douyin: bool = False) -> None:
        self.batch_size = batch_size
        self.reader = FileReader()
        self.processor = LinkProcessor(only_douyin=only_douyin)
        self.writer = Writer()

    def process_folder(
        self,
        input_dir: str | Path,
        output_dir: str | Path = DEFAULT_OUTPUT_DIR,
        reset_output: bool = False,
    ) -> dict:
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"Input folder does not exist: {input_path}")
        if not input_path.is_dir():
            raise NotADirectoryError(f"Input path is not a folder: {input_path}")

        output_path.mkdir(parents=True, exist_ok=True)

        if reset_output:
            self._reset_output(output_path)

        manifest_store = ManifestStore(output_path)
        processed_manifest = manifest_store.load()

        existing_records = self._load_existing_records(output_path / "cleaned_links.csv")
        existing_records = self._dedupe_records(existing_records)
        existing_urls = {record.url for record in existing_records}
        next_index = self._get_next_index(existing_records)

        files = self._find_supported_files(input_path)
        processed_files: list[dict] = []
        skipped_files: list[str] = []
        failed_files: list[dict] = []
        new_records: list[LinkRecord] = []

        for file_path in files:
            signature = manifest_store.get_signature(file_path)
            if manifest_store.is_processed(signature, processed_manifest):
                skipped_files.append(str(file_path))
                continue

            try:
                text = self.reader.read(file_path)
                extracted_links = self.processor.extract_links(text)
                unique_links = self.processor.deduplicate(extracted_links)

                added_count = 0
                for url in unique_links:
                    if url in existing_urls:
                        continue

                    batch_no = ((next_index - 1) // self.batch_size) + 1
                    record = LinkRecord(
                        index=next_index,
                        url=url,
                        source_file=file_path.name,
                        is_douyin=self.processor.is_douyin_url(url),
                        batch_no=batch_no,
                    )
                    new_records.append(record)
                    existing_urls.add(url)
                    next_index += 1
                    added_count += 1

                processed_manifest[signature["path"]] = signature
                processed_files.append(
                    {
                        "file": str(file_path),
                        "added_links": added_count,
                        "extracted_links": len(extracted_links),
                    }
                )
            except Exception as exc:
                failed_files.append({"file": str(file_path), "error": str(exc)})

        all_records = self._dedupe_records(existing_records + new_records)

        self.writer.save_cleaned_csv(all_records, output_path / "cleaned_links.csv")
        self.writer.save_summary(
            records=all_records,
            output_file=output_path / "summary.json",
            processed_files=processed_files,
            skipped_files=skipped_files,
            failed_files=failed_files,
            new_records=new_records,
            batch_size=self.batch_size,
        )
        self.writer.save_batches(all_records, output_path / "batches")
        manifest_store.save(processed_manifest)

        return {
            "input_dir": str(input_path),
            "output_dir": str(output_path),
            "reset_output": reset_output,
            "found_files": len(files),
            "processed_files": len(processed_files),
            "skipped_files": len(skipped_files),
            "failed_files": len(failed_files),
            "new_links_added": len(new_records),
            "total_links": len(all_records),
            "total_batches": max((record.batch_no for record in all_records), default=0),
        }

    def _find_supported_files(self, input_dir: Path) -> list[Path]:
        files = []
        for file_path in input_dir.iterdir():
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            files.append(file_path)
        return sorted(files, key=lambda p: p.name.lower())

    def _load_existing_records(self, file_path: Path) -> list[LinkRecord]:
        if not file_path.exists():
            return []

        import csv

        records = []
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(
                    LinkRecord(
                        index=int(row["index"]),
                        url=row["url"],
                        source_file=row["source_file"],
                        is_douyin=str(row["is_douyin"]).lower() == "true",
                        batch_no=int(row["batch_no"]),
                        status=row.get("status", "pending"),
                    )
                )
        return records

    @staticmethod
    def _dedupe_records(records: list[LinkRecord]) -> list[LinkRecord]:
        seen_urls: set[str] = set()
        unique_records: list[LinkRecord] = []

        for record in records:
            if record.url in seen_urls:
                continue

            seen_urls.add(record.url)
            unique_records.append(record)

        return unique_records

    @staticmethod
    def _get_next_index(existing_records: list[LinkRecord]) -> int:
        if not existing_records:
            return 1
        return max(record.index for record in existing_records) + 1

    @staticmethod
    def _reset_output(output_path: Path) -> None:
        targets = [
            output_path / "cleaned_links.csv",
            output_path / "summary.json",
            output_path / "processed_files.json",
        ]

        for target in targets:
            if target.exists():
                target.unlink()

        batch_dir = output_path / "batches"
        if batch_dir.exists():
            shutil.rmtree(batch_dir)

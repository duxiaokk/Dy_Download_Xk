from dataclasses import dataclass


@dataclass
class LinkRecord:
    index: int
    url: str
    source_file: str
    is_douyin: bool
    batch_no: int
    status: str = "pending"

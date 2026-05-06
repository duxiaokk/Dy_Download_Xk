from pathlib import Path
import re


DEFAULT_INPUT_DIR = Path(r"D:\Python\Dy_Downloads\links")
DEFAULT_OUTPUT_DIR = Path(r"D:\Python\Dy_Downloads\output")

SUPPORTED_EXTENSIONS = {".txt", ".csv"}

URL_PATTERN = re.compile(
    r"https?://[^\s\u3002\uff0c\uff1b;、）)\]<>\"']+",
    re.IGNORECASE,
)

DOUYIN_HOST_KEYWORDS = (
    "douyin.com",
    "v.douyin.com",
    "iesdouyin.com",
)

TRAILING_URL_CHARS = " \t\r\n\u3002\uff0c\uff1b;、.!?)]}>\"'"

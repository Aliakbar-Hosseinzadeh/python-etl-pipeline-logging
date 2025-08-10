"""
logging_utils.py

Production logging helpers for the ETL app:

- JsonFormatter: JSONL with UTC ISO timestamps; merges extras safely
- NonErrorFilter: allow only DEBUG/INFO/WARNING (used for stdout split)
- SafeRotatingFileHandler: rotating file handler that ensures parent folder exists
"""
from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timezone
from typing import Final, Dict, Any

# LogRecord attributes already standard; don't duplicate them in extras
LOG_RECORD_BUILTIN_ATTRS: Final[set[str]] = {
    "args","asctime","created","exc_info","exc_text","filename","funcName",
    "levelname","levelno","lineno","module","msecs","message","msg","name",
    "pathname","process","processName","relativeCreated","stack_info",
    "thread","threadName","taskName",
}

class JsonFormatter(logging.Formatter):
    """Emit one JSON object per line (JSONL) with UTC ISO timestamp."""
    def __init__(self, *, fmt_keys: Dict[str, str] | None = None) -> None:
        super().__init__()
        self.fmt_keys = fmt_keys or {}

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {}

        always = {
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = record.stack_info  # already string

        # mapped fields
        for out_key, rec_attr in self.fmt_keys.items():
            if rec_attr in always:
                payload[out_key] = always.pop(rec_attr)
            else:
                payload[out_key] = getattr(record, rec_attr, None)

        # any remaining always fields
        payload.update(always)

        # include extras (anything custom added via extra=...)
        for k, v in record.__dict__.items():
            if k not in LOG_RECORD_BUILTIN_ATTRS and k not in payload:
                payload[k] = v

        return json.dumps(payload, ensure_ascii=False, default=str)

class NonErrorFilter(logging.Filter):
    """Pass only non-error records: DEBUG/INFO/WARNING."""
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR

class SafeRotatingFileHandler(RotatingFileHandler):
    """Rotating file handler that ensures the parent directory exists."""
    def __init__(self, filename: str, *args, **kwargs) -> None:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(filename, *args, **kwargs)

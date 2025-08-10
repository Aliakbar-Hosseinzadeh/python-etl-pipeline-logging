"""
main.py

Entrypoint for the ETL app.

- Loads dictConfig from src/config/logging.json
- Rewrites any file handler 'filename' to an ABSOLUTE path under ../logs
  so logs always land in the top-level 'logs' folder regardless of CWD
- Installs a named QueueHandler ('queue_handler') and starts its listener
- Keeps the split: non-errors → stdout, errors → stderr
- Writes all levels to logs/app.log.jsonl
"""
from __future__ import annotations

import atexit
import json
import logging
import logging.config
from pathlib import Path

from config import install_queue_handler  # from src/config/__init__.py

APP_DIR = Path(__file__).resolve().parent         # .../src
PROJECT_ROOT = APP_DIR.parent                     # .../
CONFIG_PATH = APP_DIR / "config" / "logging.json" # .../src/config/logging.json
LOGS_ROOT = PROJECT_ROOT / "logs"                 # .../logs

logger = logging.getLogger("etl")  # stable name for dashboards

def _absolutize_file_handler_paths(cfg: dict) -> None:
    """
    Ensure any handler with 'filename' writes under PROJECT_ROOT/logs.
    """
    handlers = cfg.get("handlers", {})
    for h in handlers.values():
        filename = h.get("filename")
        if filename:
            abs_path = (LOGS_ROOT / Path(filename).name).resolve()
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            h["filename"] = str(abs_path)

def setup_logging() -> None:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Make file handler path absolute to ../logs regardless of where we run from
    _absolutize_file_handler_paths(cfg)

    logging.config.dictConfig(cfg)

    # Wrap handlers behind a named QueueHandler + start its listener
    qh = install_queue_handler()
    if qh is not None and hasattr(qh, "listener"):
        qh.listener.start()                 # type: ignore[attr-defined]
        atexit.register(qh.listener.stop)   # type: ignore[attr-defined]

def run_etl() -> None:
    logger.info("ETL started", extra={"job_id": "demo-2025-08-10"})
    logger.debug("Extract step started")
    logger.info("Transform step started")
    logger.warning("Transform encountered a non-fatal issue", extra={"row": 42})
    try:
        _ = 1 / 0
    except ZeroDivisionError:
        logger.exception("Load failed")
    logger.critical("Critical state — manual intervention required")
    logger.info("ETL finished")

def main() -> None:
    setup_logging()
    run_etl()

if __name__ == "__main__":
    main()

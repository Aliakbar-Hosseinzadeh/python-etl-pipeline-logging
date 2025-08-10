"""
logger_config.py

Queue installer:
- Wraps existing root handlers (from dictConfig) behind a QueueHandler
- Names it "queue_handler" so logging.getHandlerByName("queue_handler") works
- Attaches a QueueListener that fans out to the original handlers
"""
from __future__ import annotations

import logging
import logging.handlers
import queue

def install_queue_handler() -> logging.Handler | None:
    """
    Replace root handlers with a QueueHandler named 'queue_handler' and attach a
    QueueListener that forwards to the original handlers.

    Returns the QueueHandler (or None if no handlers were configured).
    """
    root = logging.getLogger()
    targets = root.handlers[:]  # handlers created by dictConfig
    if not targets:
        return None

    q = queue.SimpleQueue() if hasattr(queue, "SimpleQueue") else queue.Queue(-1)
    qh = logging.handlers.QueueHandler(q)

    # Give it a name so logging.getHandlerByName("queue_handler") can find it
    if hasattr(qh, "set_name"):        # Python 3.12+
        qh.set_name("queue_handler")
    else:
        qh.name = "queue_handler"      # fallback

    listener = logging.handlers.QueueListener(q, *targets, respect_handler_level=True)
    qh.listener = listener  # type: ignore[attr-defined]

    # Swap: root now only has the queue handler
    root.handlers.clear()
    root.addHandler(qh)
    return qh

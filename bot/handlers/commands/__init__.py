"""Command handlers submodule.

Re-exports handlers from start_handler for organized imports.
"""

from handlers.start_handler import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)

__all__ = [
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_start",
]

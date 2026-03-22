#!/usr/bin/env python3
"""Telegram bot entry point with --test mode for offline verification.

Usage:
    uv run bot.py --test "/start"     # Test mode: prints response to stdout
    uv run bot.py                     # Telegram mode: runs the bot
"""

import asyncio
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers.start_handler import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)


# Command router: maps command names to handler functions
COMMAND_HANDLERS = {
    "start": handle_start,
    "help": handle_help,
    "health": handle_health,
    "labs": handle_labs,
    "scores": handle_scores,
}


async def run_test_mode(command: str) -> None:
    """Run a command in test mode (no Telegram connection).

    Args:
        command: Command string like "/start" or "/scores lab-04"
    """
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lstrip("/").lower()
    arg = parts[1] if len(parts) > 1 else ""

    # Get handler for this command
    handler = COMMAND_HANDLERS.get(cmd)
    if not handler:
        print(f"Unknown command: {command}\n\nUse /help to see available commands.")
        sys.exit(0)  # Don't crash - just inform the user

    # Call handler (user_id=0 for test mode)
    response = await handler(user_id=0, text=arg)
    print(response)


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode (requires BOT_TOKEN)."""
    # TODO: Task 2 — implement Telegram bot startup
    print("Telegram mode not yet implemented (Task 2)")
    print("For now, use --test mode to verify handlers.")


async def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <command>")
            print("Example: uv run bot.py --test '/start'")
            sys.exit(1)
        command = " ".join(sys.argv[2:])
        await run_test_mode(command)
    else:
        await run_telegram_mode()


if __name__ == "__main__":
    asyncio.run(main())

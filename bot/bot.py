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
    handle_message,
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
    """Run a command in test mode (no Telegram connection)."""
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    first_part = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    # Check if it's a slash command
    if first_part.startswith('/'):
        cmd = first_part.lstrip("/").lower()
        if cmd in COMMAND_HANDLERS:
            handler = COMMAND_HANDLERS[cmd]
            response = await handler(user_id=0, text=arg)
            print(response)
            return
        else:
            # Unknown command
            print(f"Unknown command: {command}\n\nUse /help to see available commands.")
            return
    else:
        # Not a slash command — treat as natural language message
        response = await handle_message(user_id=0, text=command)
        print(response)


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode (requires BOT_TOKEN)."""
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        from config import Config
        
        if not Config.BOT_TOKEN:
            print("ERROR: BOT_TOKEN not set. Check .env.bot.secret")
            sys.exit(1)
        
        # Create application
        app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(handle_start(u.effective_user.id))))
        app.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(handle_help(u.effective_user.id))))
        app.add_handler(CommandHandler("health", lambda u, c: u.message.reply_text(handle_health(u.effective_user.id))))
        app.add_handler(CommandHandler("labs", lambda u, c: u.message.reply_text(handle_labs(u.effective_user.id))))
        app.add_handler(CommandHandler("scores", lambda u, c: u.message.reply_text(handle_scores(u.effective_user.id, c.args[0] if c.args else ""))))
        
        # Add handler for regular messages (not commands)
        async def text_handler(update, context):
            user_message = update.message.text
            response = await handle_message(user_id=update.effective_user.id, text=user_message)
            await update.message.reply_text(response)
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        
        print("Bot is running... Press Ctrl+C to stop.")
        await app.run_polling()
        
    except ImportError:
        print("ERROR: python-telegram-bot not installed. Run: uv sync")
        sys.exit(1)


async def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <command>")
            print("Example: uv run bot.py --test '/start'")
            print("Example: uv run bot.py --test 'what labs are available'")
            sys.exit(1)
        command = " ".join(sys.argv[2:])
        await run_test_mode(command)
    else:
        await run_telegram_mode()


if __name__ == "__main__":
    asyncio.run(main())

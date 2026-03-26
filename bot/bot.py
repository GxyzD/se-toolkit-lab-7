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
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        from config import Config
        
        if not Config.BOT_TOKEN:
            print("ERROR: BOT_TOKEN not set. Check .env.bot.secret")
            sys.exit(1)
        
        # Create application
        app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Command handlers
        async def start_command(update, context):
            keyboard = [
                [InlineKeyboardButton("📋 Labs", callback_data="labs"),
                 InlineKeyboardButton("📊 Scores", callback_data="scores_menu")],
                [InlineKeyboardButton("ℹ️ Health", callback_data="health"),
                 InlineKeyboardButton("❓ Help", callback_data="help")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Welcome to LMS Bot! Choose an option:",
                reply_markup=reply_markup
            )
        
        async def help_command(update, context):
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "/start - Welcome\n"
                "/help - This help\n"
                "/health - Backend status\n"
                "/labs - List labs\n"
                "/scores <lab> - Scores for a lab",
                reply_markup=reply_markup
            )
        
        async def health_command(update, context):
            response = await handle_health(update.effective_user.id)
            await update.message.reply_text(response)
        
        async def labs_command(update, context):
            response = await handle_labs(update.effective_user.id)
            await update.message.reply_text(response)
        
        async def scores_command(update, context):
            arg = context.args[0] if context.args else ""
            response = await handle_scores(update.effective_user.id, arg)
            await update.message.reply_text(response)
        
        # Callback query handler for buttons
        async def button_callback(update, context):
            query = update.callback_query
            await query.answer()
            
            data = query.data
            if data == "labs":
                response = await handle_labs(query.from_user.id)
                await query.edit_message_text(response)
            elif data == "health":
                response = await handle_health(query.from_user.id)
                await query.edit_message_text(response)
            elif data == "help":
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "/start - Welcome\n"
                    "/help - This help\n"
                    "/health - Backend status\n"
                    "/labs - List labs\n"
                    "/scores <lab> - Scores for a lab",
                    reply_markup=reply_markup
                )
            elif data == "scores_menu":
                keyboard = [
                    [InlineKeyboardButton("Lab 04", callback_data="scores_lab-04"),
                     InlineKeyboardButton("Lab 05", callback_data="scores_lab-05")],
                    [InlineKeyboardButton("Lab 06", callback_data="scores_lab-06"),
                     InlineKeyboardButton("Lab 07", callback_data="scores_lab-07")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("Select a lab:", reply_markup=reply_markup)
            elif data.startswith("scores_lab-"):
                lab = data.replace("scores_", "")
                response = await handle_scores(query.from_user.id, lab)
                await query.edit_message_text(response)
            elif data == "back":
                keyboard = [
                    [InlineKeyboardButton("📋 Labs", callback_data="labs"),
                     InlineKeyboardButton("📊 Scores", callback_data="scores_menu")],
                    [InlineKeyboardButton("ℹ️ Health", callback_data="health"),
                     InlineKeyboardButton("❓ Help", callback_data="help")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("Welcome back! Choose an option:", reply_markup=reply_markup)
        
        # Register handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("health", health_command))
        app.add_handler(CommandHandler("labs", labs_command))
        app.add_handler(CommandHandler("scores", scores_command))
        
        # Message handler for natural language
        async def text_handler(update, context):
            user_message = update.message.text
            response = await handle_message(user_id=update.effective_user.id, text=user_message)
            await update.message.reply_text(response)
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        app.add_handler(CallbackQueryHandler(button_callback))
        
        print("Bot is running... Press Ctrl+C to stop.")
        
        # Start the bot
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
            
    except ImportError as e:
        print(f"ERROR: {e}. Run: uv add python-telegram-bot")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")
        sys.exit(0)

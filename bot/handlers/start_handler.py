"""Command handlers for the Telegram bot.

Handlers are pure functions: they take input and return text.
They don't know about Telegram — same logic works from --test mode,
unit tests, or the actual Telegram bot.
"""


async def handle_start(user_id: int, text: str) -> str:
    """Handle /start command.

    Args:
        user_id: Telegram user ID (used for personalization later)
        text: Raw message text (ignored for /start)

    Returns:
        Welcome message
    """
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check system health, browse labs, and view scores.\n\n"
        "Available commands:\n"
        "/help — Show this help message\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — View scores for a lab"
    )


async def handle_help(user_id: int, text: str) -> str:
    """Handle /help command.

    Args:
        user_id: Telegram user ID
        text: Raw message text

    Returns:
        List of available commands
    """
    return (
        "📚 LMS Bot — Available Commands\n\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — View scores (e.g., /scores lab-04)"
    )


async def handle_health(user_id: int, text: str) -> str:
    """Handle /health command.

    Args:
        user_id: Telegram user ID
        text: Raw message text

    Returns:
        Backend health status (placeholder for Task 2)
    """
    # TODO: Task 2 — call backend /health endpoint
    return "🔍 Backend health check — placeholder (Task 2)"


async def handle_labs(user_id: int, text: str) -> str:
    """Handle /labs command.

    Args:
        user_id: Telegram user ID
        text: Raw message text

    Returns:
        List of available labs (placeholder for Task 2)
    """
    # TODO: Task 2 — call backend /items endpoint
    return "📋 Available labs — placeholder (Task 2)"


async def handle_scores(user_id: int, text: str) -> str:
    """Handle /scores command.

    Args:
        user_id: Telegram user ID
        text: Raw message text (e.g., "lab-04")

    Returns:
        Scores for the specified lab (placeholder for Task 2)
    """
    # TODO: Task 2 — call backend /analytics endpoint
    lab_name = text.strip() if text.strip() else "<no lab specified>"
    return f"📊 Scores for {lab_name} — placeholder (Task 2)"

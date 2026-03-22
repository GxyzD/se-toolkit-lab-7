"""Command handlers for the Telegram bot.

Handlers are pure functions: they take input and return text.
They don't know about Telegram — same logic works from --test mode,
unit tests, or the actual Telegram bot.
"""

import re
import httpx
from config import config
from services.api_client import LMSAPIClient

# Shared API client instance
_api_client = LMSAPIClient(config.lms_api_base_url, config.lms_api_key)


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
        Backend health status
    """
    try:
        items = await _api_client.get("/items/")
        count = len(items) if isinstance(items, list) else "unknown"
        return f"✅ Health OK. Backend running with {count} items."
    except (ConnectionError, httpx.HTTPStatusError, Exception) as e:
        return _api_client.format_error_message(e)


async def handle_labs(user_id: int, text: str) -> str:
    """Handle /labs command.

    Args:
        user_id: Telegram user ID
        text: Raw message text (optional filter)

    Returns:
        List of available labs
    """
    try:
        items = await _api_client.get("/items/")
        if not items or not isinstance(items, list):
            return "📋 No labs available."

        # Filter only labs (not tasks) and count tasks by parent_id
        labs = [item for item in items if item.get("type") == "lab"]
        
        # Count tasks per lab
        task_counts = {}
        for item in items:
            if item.get("type") == "task":
                parent_id = item.get("parent_id")
                if parent_id:
                    task_counts[parent_id] = task_counts.get(parent_id, 0) + 1

        # Parse filter if provided (e.g., "lab", "project")
        filter_type = text.strip().lower() if text.strip() else ""

        lines = ["📚 Available labs:"]
        for lab in labs:
            # Filter by title if specified
            if filter_type and filter_type not in lab.get("title", "").lower():
                continue
            title = lab.get("title", "Unknown")
            lab_id = lab.get("id")
            task_count = task_counts.get(lab_id, 0)
            lines.append(f"- {title} ({task_count} tasks)")

        return "\n".join(lines)
    except (ConnectionError, httpx.HTTPStatusError, Exception) as e:
        return _api_client.format_error_message(e)


async def handle_scores(user_id: int, text: str) -> str:
    """Handle /scores command.

    Args:
        user_id: Telegram user ID
        text: Raw message text (e.g., "lab-04")

    Returns:
        Scores for the specified lab
    """
    lab_name = text.strip() if text.strip() else ""

    if not lab_name:
        return "📊 Please specify a lab. Example: /scores lab-04"

    try:
        # First check if the lab exists
        items = await _api_client.get("/items/")
        labs = [item for item in items if item.get("type") == "lab"]
        
        lab_found = False
        lab_display_name = lab_name

        for lab in labs:
            title = lab.get("title", "").lower()
            # Match by slug pattern (lab-04 -> Lab 04) or by title
            # Extract lab number from title like "lab 04" or "lab 4"
            lab_num_match = re.search(r'lab\s*(\d+)', title)
            input_num_match = re.search(r'lab[- ]?(\d+)', lab_name.lower())
            
            if input_num_match and lab_num_match:
                if input_num_match.group(1) == lab_num_match.group(1):
                    lab_found = True
                    lab_display_name = lab.get("title", lab_name)
                    break
            elif lab_name.lower() in title:
                lab_found = True
                lab_display_name = lab.get("title", lab_name)
                break

        if not lab_found:
            # Lab not found - suggest available labs
            available = [lab.get("title", "unknown") for lab in labs]
            return f"📊 Lab '{lab_name}' not found.\n\nAvailable labs: {', '.join(available)}"

        # Get pass rates for the lab
        pass_rates = await _api_client.get("/analytics/pass-rates", params={"lab": lab_name})

        if not pass_rates or not isinstance(pass_rates, list):
            return f"📊 No scores available for {lab_display_name}."

        lines = [f"📈 Pass rates for {lab_display_name}:"]
        for rate in pass_rates:
            task_name = rate.get("task", "Unknown task")
            avg_score = rate.get("avg_score", 0)
            attempts = rate.get("attempts", 0)
            lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")

        return "\n".join(lines)
    except (ConnectionError, httpx.HTTPStatusError, Exception) as e:
        return _api_client.format_error_message(e)

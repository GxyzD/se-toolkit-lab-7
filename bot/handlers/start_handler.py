"""Handlers for bot commands."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from services.lms_client import LMSClient


_client = None


def get_client():
    global _client
    if _client is None:
        _client = LMSClient()
    return _client


async def handle_start(user_id: int, text: str = "") -> str:
    return "Welcome to the LMS Bot! Use /help to see available commands."


async def handle_help(user_id: int, text: str = "") -> str:
    return (
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List all labs\n"
        "/scores <lab> - Get pass rates for a lab"
    )


async def handle_health(user_id: int, text: str = "") -> str:
    client = get_client()
    result = client.get_items()
    if result is None:
        return "Backend error: connection refused."
    if 'error' in result:
        return f"Backend error: {result['error']}"
    if isinstance(result, list):
        return f"Backend is healthy. {len(result)} items available."
    return "Backend is healthy."


async def handle_labs(user_id: int, text: str = "") -> str:
    client = get_client()
    result = client.get_items()
    if result is None or 'error' in result:
        return "Error: Cannot fetch labs."
    if not isinstance(result, list):
        return "Error: Unexpected response."
    labs_list = [item for item in result if item.get('type') == 'lab']
    if not labs_list:
        return "No labs found."
    lines = []
    for lab in labs_list:
        lab_id = lab.get('id', '')
        name = lab.get('name')
        desc = lab.get('description', '')
        if name and name != 'null':
            title = name
        elif lab_id:
            match = re.search(r'lab-(\d+)', lab_id)
            if match:
                title = f"Lab {match.group(1)}"
            else:
                title = lab_id
        else:
            title = "Unknown Lab"
        lines.append(f"{title} — {desc}" if desc else title)
    return "\n".join(lines)


async def handle_scores(user_id: int, text: str = "") -> str:
    lab_id = text.strip()
    if not lab_id:
        return "Error: Please specify a lab ID. Example: /scores lab-04"
    if not re.match(r'lab-\d{2}', lab_id):
        match = re.search(r'(\d+)', lab_id)
        if match:
            lab_id = f"lab-{int(match.group(1)):02d}"
    client = get_client()
    result = client.get_pass_rates(lab_id)
    if result is None:
        return f"Error: Cannot connect for {lab_id}."
    if 'error' in result:
        return f"Error: {result['error']}"
    pass_rates = result.get('pass_rates') or result.get('data') or result.get('items')
    if not pass_rates:
        return f"No data for {lab_id}."
    lines = [f"Pass rates for {lab_id}:"]
    for item in pass_rates:
        if isinstance(item, dict):
            task = item.get('task_name') or item.get('name') or 'Task'
            rate = item.get('pass_rate') or item.get('rate') or 0
            attempts = item.get('attempts') or ''
            if attempts:
                lines.append(f"- {task}: {rate:.1f}% ({attempts} attempts)")
            else:
                lines.append(f"- {task}: {rate:.1f}%")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


async def handle_message(user_id: int, text: str = "") -> str:
    from router import IntentRouter
    router = IntentRouter()
    return router.route(text)

# Development Plan for Lab 7 Bot

## Task 1: Plan and Scaffold (this task)
- Create bot directory structure
- Implement entry point with `--test` mode
- Create handler modules
- Set up dependencies in pyproject.toml
- Test with `uv run bot.py --test "/command"`
- Deploy and verify in Telegram

## Task 2: Backend Integration
- Connect to LMS API via `services/lms_client.py`
- Implement handlers that fetch real data:
  - `/health` – check backend status
  - `/labs` – list available labs
  - `/scores <lab>` – get scores for a lab
- Use LMS_API_KEY from environment

## Task 3: Intent Routing
- Integrate LLM (Qwen Code API) to understand user intent
- Classify messages into:
  - Command (existing bot commands)
  - Question (needs answer from wiki or code)
- Use `llm_client.py` to call LLM
- Implement fallback when intent is unclear

## Task 4: System Agent
- Add tools for the LLM to answer questions:
  - `query_api` – get live data from backend
  - `read_file` – read project files
  - `list_files` – explore directory structure
- Implement agentic loop (same as Lab 6 Task 2)
- Respond with answers based on system state

## Task 5: Deployment & Polish
- Ensure bot runs reliably on VM
- Add error handling and logging
- Verify all commands work in Telegram
- Final testing with autochecker

## Architecture Decisions
- **Testable handlers**: All command logic is separate from Telegram transport.
- **`--test` mode**: Calls handlers directly, prints to stdout.
- **Configuration**: All secrets in `.env.bot.secret`, not hardcoded.
- **Dependencies**: Use `pyproject.toml` and `uv`, no `requirements.txt`.

## Tools Used
- `python-telegram-bot` (v21+) for Telegram integration
- `requests` for HTTP calls to backend
- `python-dotenv` for environment variables
- `uv` for dependency management
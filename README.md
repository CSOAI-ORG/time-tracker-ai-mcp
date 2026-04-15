# Time Tracker Ai

> By [MEOK AI Labs](https://meok.ai) — Track work time with start/stop timers, log entries, and generate reports. By MEOK AI Labs.

Time Tracker AI — track work time, manage projects, and generate productivity reports. MEOK AI Labs.

## Installation

```bash
pip install time-tracker-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install time-tracker-ai-mcp
```

## Tools

### `start_timer`
Start a time tracking timer for a project. Optionally add a task description and comma-separated tags.

**Parameters:**
- `project` (str)
- `task` (str)
- `tags` (str)

### `stop_timer`
Stop the running timer and log the time entry. Optionally add notes.

**Parameters:**
- `notes` (str)

### `get_report`
Generate a time report. Optionally filter by project. Shows totals per project and per day.

**Parameters:**
- `project` (str)
- `days` (int)

### `list_entries`
List recent time entries. Optionally filter by project. Returns up to limit entries (default 20).

**Parameters:**
- `project` (str)
- `limit` (int)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/time-tracker-ai-mcp](https://github.com/CSOAI-ORG/time-tracker-ai-mcp)
- **PyPI**: [pypi.org/project/time-tracker-ai-mcp](https://pypi.org/project/time-tracker-ai-mcp/)

## License

MIT — MEOK AI Labs

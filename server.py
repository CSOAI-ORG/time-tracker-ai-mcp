#!/usr/bin/env python3
"""Time Tracker AI — track work time, manage projects, and generate productivity reports. MEOK AI Labs."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access
from persistence import ServerStore

import json
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

_store = ServerStore("time-tracker-ai")

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("time-tracker-ai", instructions="Track work time with start/stop timers, log entries, and generate reports. By MEOK AI Labs.")


@mcp.tool()
def start_timer(project: str, task: str = "", tags: str = "", api_key: str = "") -> str:
    """Start a time tracking timer for a project. Optionally add a task description and comma-separated tags."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    active_timer = _store.get("active_timer")
    if active_timer:
        return json.dumps({
            "error": "Timer already running. Stop it first.",
            "active_timer": active_timer,
        })
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    active_timer = {
        "project": project,
        "task": task or "General",
        "tags": tag_list,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    _store.set("active_timer", active_timer)
    # Count today's entries for context
    today = datetime.now(timezone.utc).date().isoformat()
    today_entries = [e for e in _store.list("entries") if e["date"] == today]
    today_hours = sum(e["hours"] for e in today_entries)
    return json.dumps({
        "status": "timer_started",
        "timer": active_timer,
        "today_so_far": {
            "entries": len(today_entries),
            "hours_logged": round(today_hours, 2),
        },
    }, indent=2)


@mcp.tool()
def stop_timer(notes: str = "", api_key: str = "") -> str:
    """Stop the running timer and log the time entry. Optionally add notes."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    active_timer = _store.get("active_timer")
    if not active_timer:
        return json.dumps({"error": "No timer running. Start one first."})
    now = datetime.now(timezone.utc)
    started = datetime.fromisoformat(active_timer["started_at"])
    duration_seconds = (now - started).total_seconds()
    hours = round(duration_seconds / 3600, 3)
    minutes = round(duration_seconds / 60, 1)
    entry = {
        "id": _store.list_length("entries") + 1,
        "project": active_timer["project"],
        "task": active_timer["task"],
        "tags": active_timer["tags"],
        "started_at": active_timer["started_at"],
        "ended_at": now.isoformat(),
        "hours": hours,
        "minutes": minutes,
        "notes": notes,
        "date": now.date().isoformat(),
    }
    _store.append("entries", entry)
    _store.delete("active_timer")
    # Project totals
    all_entries = _store.list("entries")
    project_total = sum(e["hours"] for e in all_entries if e["project"] == entry["project"])
    return json.dumps({
        "status": "timer_stopped",
        "entry": entry,
        "project_total_hours": round(project_total, 2),
        "all_entries_count": len(all_entries),
    }, indent=2)


@mcp.tool()
def get_report(project: str = "", days: int = 7, api_key: str = "") -> str:
    """Generate a time report. Optionally filter by project. Shows totals per project and per day."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    all_entries = _store.list("entries")
    if not all_entries:
        return json.dumps({"message": "No time entries yet. Start tracking!", "entries": 0})
    entries = all_entries
    if project:
        entries = [e for e in entries if e["project"].lower() == project.lower()]
        if not entries:
            return json.dumps({"message": f"No entries found for project '{project}'", "entries": 0})
    total_hours = sum(e["hours"] for e in entries)
    # By project
    by_project: dict[str, float] = defaultdict(float)
    for e in entries:
        by_project[e["project"]] += e["hours"]
    project_breakdown = sorted(
        [{"project": p, "hours": round(h, 2), "pct": round(h / total_hours * 100, 1)} for p, h in by_project.items()],
        key=lambda x: x["hours"], reverse=True,
    )
    # By date
    by_date: dict[str, float] = defaultdict(float)
    for e in entries:
        by_date[e["date"]] += e["hours"]
    daily_breakdown = sorted(
        [{"date": d, "hours": round(h, 2)} for d, h in by_date.items()],
        key=lambda x: x["date"], reverse=True,
    )[:days]
    # Tags summary
    tag_hours: dict[str, float] = defaultdict(float)
    for e in entries:
        for tag in e.get("tags", []):
            tag_hours[tag] += e["hours"]
    top_tags = sorted(tag_hours.items(), key=lambda x: x[1], reverse=True)[:10]
    avg_daily = total_hours / max(len(by_date), 1)
    return json.dumps({
        "total_entries": len(entries),
        "total_hours": round(total_hours, 2),
        "average_daily_hours": round(avg_daily, 2),
        "by_project": project_breakdown,
        "by_date": daily_breakdown,
        "top_tags": [{"tag": t, "hours": round(h, 2)} for t, h in top_tags] if top_tags else [],
        "active_timer": _active_timer,
    }, indent=2)


@mcp.tool()
def list_entries(project: str = "", limit: int = 20, api_key: str = "") -> str:
    """List recent time entries. Optionally filter by project. Returns up to limit entries (default 20)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    entries = _entries
    if project:
        entries = [e for e in entries if e["project"].lower() == project.lower()]
    limit = max(1, min(limit, 100))
    recent = list(reversed(entries))[:limit]
    total = sum(e["hours"] for e in entries)
    return json.dumps({
        "entries": recent,
        "showing": len(recent),
        "total_entries": len(entries),
        "total_hours": round(total, 2),
        "filter_project": project or "all",
        "active_timer": _active_timer,
    }, indent=2)


if __name__ == "__main__":
    mcp.run()

import time
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("time-tracker")

SESSIONS = []
ACTIVE_TIMER = None

@mcp.tool()
def start_timer(project: str, task: str = "") -> dict:
    """Start a timer."""
    global ACTIVE_TIMER
    ACTIVE_TIMER = {"project": project, "task": task, "start": time.time()}
    return {"status": "started", "timer": ACTIVE_TIMER}

@mcp.tool()
def stop_timer() -> dict:
    """Stop the active timer."""
    global ACTIVE_TIMER
    if ACTIVE_TIMER is None:
        return {"error": "No active timer"}
    duration = time.time() - ACTIVE_TIMER["start"]
    session = {
        "project": ACTIVE_TIMER["project"],
        "task": ACTIVE_TIMER["task"],
        "duration_seconds": round(duration, 1),
        "duration_hours": round(duration / 3600, 3),
    }
    SESSIONS.append(session)
    ACTIVE_TIMER = None
    return {"status": "stopped", "session": session}

@mcp.tool()
def get_summary(project: str = None) -> dict:
    """Summarize tracked time."""
    filtered = [s for s in SESSIONS if project is None or s["project"] == project]
    total_seconds = sum(s["duration_seconds"] for s in filtered)
    total_hours = round(total_seconds / 3600, 3)
    by_project = {}
    for s in filtered:
        by_project.setdefault(s["project"], 0.0)
        by_project[s["project"]] += s["duration_seconds"]
    by_project_hours = {k: round(v / 3600, 3) for k, v in by_project.items()}
    return {"total_hours": total_hours, "session_count": len(filtered), "by_project_hours": by_project_hours}

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

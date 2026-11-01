import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]

HISTORY_FILE = (
    PROJECT_ROOT / "results" / "audit_history.json"
)


def load_audit_history():
    """Load previously saved audit records."""

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

        return history if isinstance(history, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_audit_history(
    analysis_type,
    summary,
):
    """Save a new audit record."""

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    history = load_audit_history()

    record = {
        "run_id": str(uuid4()),
        "analysis_type": analysis_type,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "summary": summary,
    }

    history.append(record)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            indent=4,
            default=str,
        )

    return record


def get_audit_history():
    """Return saved records, newest first."""

    history = load_audit_history()

    return sorted(
        history,
        key=lambda item: item.get("timestamp", ""),
        reverse=True,
    )

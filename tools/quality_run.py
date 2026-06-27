#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


EVENTS_DIR = Path("quality/events")


def now() -> datetime:
    return datetime.now().astimezone()


def now_iso() -> str:
    return now().isoformat(timespec="seconds")


def safe_task_id(task_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", task_id)


def create_log_path(task_id: str) -> Path:
    timestamp = now().strftime("%Y%m%dT%H%M%S")
    safe_id = safe_task_id(task_id)
    return EVENTS_DIR / f"{timestamp}_{safe_id}.jsonl"


def write_event(log_path: Path, event: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a quality check command and record the result."
    )
    parser.add_argument("--task-id", required=True, help="Task ID for this quality run.")
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute. Example: -- python -m pytest",
    )

    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        raise SystemExit(
            "command is required. Example: python tools/quality_run.py --task-id sample -- python -m pytest"
        )

    log_path = create_log_path(args.task_id)

    write_event(
        log_path,
        {
            "task_id": args.task_id,
            "event": "test_run_started",
            "command": command,
            "timestamp": now_iso(),
        },
    )

    result = subprocess.run(command)

    write_event(
        log_path,
        {
            "task_id": args.task_id,
            "event": "test_passed" if result.returncode == 0 else "test_failed",
            "exit_code": result.returncode,
            "timestamp": now_iso(),
        },
    )

    print(f"quality log: {log_path}")

    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

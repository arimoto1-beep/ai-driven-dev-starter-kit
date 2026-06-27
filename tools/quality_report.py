#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path


EVENTS_DIR = Path("quality/events")
REPORT_PATH = Path("quality/report.md")


def load_events() -> list[dict]:
    if not EVENTS_DIR.exists():
        return []

    events = []

    for path in sorted(EVENTS_DIR.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                event = json.loads(line)
                event["_source_file"] = str(path)
                events.append(event)

    return events


def main() -> None:
    events = load_events()

    task_events: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        task_id = event.get("task_id", "UNKNOWN")
        task_events[task_id].append(event)

    total_tasks = len(task_events)
    executed_tasks = 0
    first_passed_tasks = 0
    first_failed_tasks = 0
    final_passed_tasks = 0
    total_test_runs = 0

    rows = []

    for task_id, items in sorted(task_events.items()):
        result_events = [
            e for e in items if e.get("event") in {"test_passed", "test_failed"}
        ]

        if not result_events:
            continue

        result_events.sort(key=lambda e: e.get("timestamp", ""))

        executed_tasks += 1
        total_test_runs += len(result_events)

        first_result = result_events[0]["event"]
        final_result = result_events[-1]["event"]

        if first_result == "test_passed":
            first_passed_tasks += 1
        else:
            first_failed_tasks += 1

        if final_result == "test_passed":
            final_passed_tasks += 1

        rows.append(
            {
                "task_id": task_id,
                "runs": len(result_events),
                "first_result": first_result,
                "final_result": final_result,
            }
        )

    avg_runs = total_test_runs / executed_tasks if executed_tasks else 0.0

    lines = []
    lines.append("# AI駆動開発 検証ログサマリ")
    lines.append("")
    lines.append("## サマリ")
    lines.append("")
    lines.append(f"- 対象タスク数: {total_tasks}")
    lines.append(f"- テスト実行済みタスク数: {executed_tasks}")
    lines.append(f"- 初回テスト通過タスク数: {first_passed_tasks}")
    lines.append(f"- 初回テスト失敗タスク数: {first_failed_tasks}")
    lines.append(f"- 最終テスト通過タスク数: {final_passed_tasks}")
    lines.append(f"- テスト実行回数: {total_test_runs}")
    lines.append(f"- タスクあたり平均テスト実行回数: {avg_runs:.2f}")
    lines.append("")
    lines.append("## タスク別結果")
    lines.append("")
    lines.append("| task_id | runs | first_result | final_result |")
    lines.append("|---|---:|---|---|")

    for row in rows:
        lines.append(
            f"| {row['task_id']} | {row['runs']} | {row['first_result']} | {row['final_result']} |"
        )

    lines.append("")
    lines.append("## 注意")
    lines.append("")
    lines.append("このサマリは、実装バグ率を示すものではありません。")
    lines.append("AI駆動開発におけるテスト実行と修正ループの証跡として利用します。")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"generated: {REPORT_PATH}")


if __name__ == "__main__":
    main()

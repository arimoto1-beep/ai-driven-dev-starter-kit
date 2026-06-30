#!/usr/bin/env python3
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


EVENTS_DIR = Path("quality/events")
REPORT_PATH = Path("quality/report.md")
DOCS_DIR = Path("docs")

FINAL_REVIEW_RESULTS = [
    "OK",
    "軽微な指摘あり",
    "要修正",
    "要仕様確認",
]

NEXT_STEP_RESULTS = [
    "GO",
    "条件付きGO",
    "STOP",
]


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


def read_section_body(text: str, heading: str) -> str:
    """
    Markdown の指定見出し配下を、次の ## 見出しまで取得する。
    """
    pattern = rf"^## {re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)

    if not match:
        return ""

    start = match.end()
    next_heading = re.search(r"^## .+$", text[start:], flags=re.MULTILINE)

    if not next_heading:
        return text[start:].strip()

    end = start + next_heading.start()
    return text[start:end].strip()


def extract_single_line_value(section_body: str, allowed_values: list[str]) -> str | None:
    """
    セクション本文から、許可された判定値の単独行を拾う。
    バッククォート付きの旧形式も一応許容する。
    """
    allowed = set(allowed_values)

    for line in section_body.splitlines():
        value = line.strip()

        if not value:
            continue

        # 旧形式の `OK` のような記述も拾えるようにする
        if value.startswith("`") and value.endswith("`"):
            value = value[1:-1].strip()

        if value in allowed:
            return value

    return None


def find_review_files() -> list[Path]:
    if not DOCS_DIR.exists():
        return []

    review_files = []
    review_files.extend(DOCS_DIR.glob("**/25_review_result.md"))
    review_files.extend(DOCS_DIR.glob("**/12_command_review_result.md"))

    return sorted(review_files)


def load_review_results() -> list[dict]:
    results = []

    for path in find_review_files():
        text = path.read_text(encoding="utf-8")

        final_section = read_section_body(text, "最終判定")
        next_step_section = read_section_body(text, "次工程移行判定")

        final_result = extract_single_line_value(
            final_section,
            FINAL_REVIEW_RESULTS,
        )
        next_step_result = extract_single_line_value(
            next_step_section,
            NEXT_STEP_RESULTS,
        )

        review_type = (
            "command/app"
            if path.name == "12_command_review_result.md"
            else "feature"
        )

        results.append(
            {
                "path": str(path),
                "review_type": review_type,
                "final_result": final_result or "未取得",
                "next_step_result": next_step_result or "未取得",
            }
        )

    return results


def build_test_summary(events: list[dict]) -> tuple[list[str], list[dict]]:
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
    lines.append("## 検証ログサマリ")
    lines.append("")
    lines.append(f"- 対象タスク数: {total_tasks}")
    lines.append(f"- テスト実行済みタスク数: {executed_tasks}")
    lines.append(f"- 初回テスト通過タスク数: {first_passed_tasks}")
    lines.append(f"- 初回テスト失敗タスク数: {first_failed_tasks}")
    lines.append(f"- 最終テスト通過タスク数: {final_passed_tasks}")
    lines.append(f"- テスト実行回数: {total_test_runs}")
    lines.append(f"- タスクあたり平均テスト実行回数: {avg_runs:.2f}")
    lines.append("")
    lines.append("### タスク別結果")
    lines.append("")
    lines.append("| task_id | runs | first_result | final_result |")
    lines.append("|---|---:|---|---|")

    if rows:
        for row in rows:
            lines.append(
                f"| {row['task_id']} | {row['runs']} | {row['first_result']} | {row['final_result']} |"
            )
    else:
        lines.append("| 該当なし | 0 | - | - |")

    lines.append("")

    return lines, rows


def build_review_summary(review_results: list[dict]) -> list[str]:
    review_type_counter = Counter(result["review_type"] for result in review_results)
    final_result_counter = Counter(result["final_result"] for result in review_results)
    next_step_result_counter = Counter(
        result["next_step_result"] for result in review_results
    )

    lines = []
    lines.append("## レビューサマリ")
    lines.append("")
    lines.append(f"- feature 単体レビュー結果数: {review_type_counter.get('feature', 0)}")
    lines.append(
        f"- command/app 全体レビュー結果数: {review_type_counter.get('command/app', 0)}"
    )
    lines.append("")

    lines.append("### 最終判定")
    lines.append("")

    for result in FINAL_REVIEW_RESULTS:
        lines.append(f"- {result}: {final_result_counter.get(result, 0)}")

    if final_result_counter.get("未取得", 0):
        lines.append(f"- 未取得: {final_result_counter.get('未取得', 0)}")

    lines.append("")

    lines.append("### 次工程移行判定")
    lines.append("")

    for result in NEXT_STEP_RESULTS:
        lines.append(f"- {result}: {next_step_result_counter.get(result, 0)}")

    if next_step_result_counter.get("未取得", 0):
        lines.append(f"- 未取得: {next_step_result_counter.get('未取得', 0)}")

    lines.append("")

    lines.append("### レビュー結果一覧")
    lines.append("")
    lines.append("| 種別 | ファイル | 最終判定 | 次工程移行判定 |")
    lines.append("|---|---|---|---|")

    if review_results:
        for result in review_results:
            lines.append(
                f"| {result['review_type']} | `{result['path']}` | {result['final_result']} | {result['next_step_result']} |"
            )
    else:
        lines.append("| 該当なし | - | - | - |")

    lines.append("")

    return lines


def main() -> None:
    events = load_events()
    review_results = load_review_results()

    lines = []
    lines.append("# AI駆動開発 品質サマリ")
    lines.append("")

    test_summary_lines, _ = build_test_summary(events)
    lines.extend(test_summary_lines)

    review_summary_lines = build_review_summary(review_results)
    lines.extend(review_summary_lines)

    lines.append("## 注意")
    lines.append("")
    lines.append("このサマリは、実装バグ率や品質保証結果を示すものではありません。")
    lines.append("AI駆動開発におけるテスト実行、修正ループ、レビュー判定の証跡として利用します。")
    lines.append("最終的な品質判断は、このサマリではなく、人間によるレビューと受け入れ判断で行います。")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"generated: {REPORT_PATH}")


if __name__ == "__main__":
    main()
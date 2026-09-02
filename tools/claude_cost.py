#!/usr/bin/env python3
"""
claude_cost.py

Estimate Claude Code API-equivalent token costs from local session transcripts.

Default:
    python claude_cost.py

Scans ~/.claude/projects recursively, analyzes today's requests (local time),
and prints:
  - total estimated API-equivalent cost
  - input / cache-read / cache-write / output cost breakdown
  - cost by project
  - cost by model
  - top 10 sessions, including first user prompt and start time

Useful options:
    --timeline                 Show request-by-request chronological cost history
    --days 7                   Analyze the last 7 x 24 hours
    --all-time                 Analyze all available local history
    --project D:\\work\\repo     Analyze one project (today by default)
    --project <log-dir>        Also accepts ~/.claude/projects/<project>
    --file <session.jsonl>     Analyze one JSONL file
    --log-dir <project-dir>    Analyze all JSONL under one Claude log directory
    --top-sessions N           Show top N sessions (0 = all; default 10)
    --top-requests N           Show top N API requests by estimated cost
    --prompt-width N           First-prompt preview width (0 = full; default 100)
    --verbose                  Show scan/dedupe/token diagnostics

No third-party packages are required. This script performs no network access.

Pricing:
    Embedded standard first-party Claude API token prices, checked 2026-09-03.
    Pricing changes over time, so update PRICE_RULES when necessary.

Important:
    This is an estimate, not a billing statement. It intentionally does not
    account for every possible modifier or non-token charge (for example fast
    mode, data-residency multipliers, server-side tool charges, cloud-provider
    pricing, negotiated discounts, or taxes).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable, Optional

VERSION = "1.0.0"
PRICING_CHECKED = "2026-09-03"


# ---------------------------------------------------------------------------
# Pricing: USD per 1 million tokens
# Columns: base input, 5m cache write, 1h cache write, cache read, output
# Source checked 2026-09-03:
# https://platform.claude.com/docs/en/about-claude/pricing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Price:
    input: float
    cache_5m: float
    cache_1h: float
    cache_read: float
    output: float


@dataclass(frozen=True)
class PriceRule:
    label: str
    pattern: re.Pattern[str]
    price: Price


def model_pattern(family: str, version: str) -> re.Pattern[str]:
    """
    Match model aliases and date-suffixed Claude API IDs, e.g.
      claude-opus-5
      claude-opus-5-20260805
      claude-sonnet-4-5
      claude-sonnet-4-5-20250929
    """
    prefix = rf"claude-{re.escape(family)}-{re.escape(version)}"
    return re.compile(rf"^{prefix}(?:-\d{{8}})?$", re.IGNORECASE)


PRICE_RULES = [
    PriceRule("Claude Fable 5.1", model_pattern("fable", "5-1"),
              Price(10.00, 12.50, 20.00, 0.25, 50.00)),
    PriceRule("Claude Mythos 5.1", model_pattern("mythos", "5-1"),
              Price(10.00, 12.50, 20.00, 0.25, 50.00)),
    PriceRule("Claude Fable 5", model_pattern("fable", "5"),
              Price(10.00, 12.50, 20.00, 1.00, 50.00)),
    PriceRule("Claude Mythos 5", model_pattern("mythos", "5"),
              Price(10.00, 12.50, 20.00, 1.00, 50.00)),

    PriceRule("Claude Opus 5", model_pattern("opus", "5"),
              Price(5.00, 6.25, 10.00, 0.50, 25.00)),
    PriceRule("Claude Opus 4.8", model_pattern("opus", "4-8"),
              Price(5.00, 6.25, 10.00, 0.50, 25.00)),
    PriceRule("Claude Opus 4.7", model_pattern("opus", "4-7"),
              Price(5.00, 6.25, 10.00, 0.50, 25.00)),
    PriceRule("Claude Opus 4.6", model_pattern("opus", "4-6"),
              Price(5.00, 6.25, 10.00, 0.50, 25.00)),
    PriceRule("Claude Opus 4.5", model_pattern("opus", "4-5"),
              Price(5.00, 6.25, 10.00, 0.50, 25.00)),
    PriceRule("Claude Opus 4.1", model_pattern("opus", "4-1"),
              Price(15.00, 18.75, 30.00, 1.50, 75.00)),
    PriceRule("Claude Opus 4", model_pattern("opus", "4"),
              Price(15.00, 18.75, 30.00, 1.50, 75.00)),

    PriceRule("Claude Sonnet 5", model_pattern("sonnet", "5"),
              Price(2.00, 2.50, 4.00, 0.20, 10.00)),
    PriceRule("Claude Sonnet 4.6", model_pattern("sonnet", "4-6"),
              Price(3.00, 3.75, 6.00, 0.30, 15.00)),
    PriceRule("Claude Sonnet 4.5", model_pattern("sonnet", "4-5"),
              Price(3.00, 3.75, 6.00, 0.30, 15.00)),
    PriceRule("Claude Sonnet 4", model_pattern("sonnet", "4"),
              Price(3.00, 3.75, 6.00, 0.30, 15.00)),

    PriceRule("Claude Haiku 4.5", model_pattern("haiku", "4-5"),
              Price(1.00, 1.25, 2.00, 0.10, 5.00)),
    PriceRule("Claude Haiku 3.5", model_pattern("haiku", "3-5"),
              Price(0.80, 1.00, 1.60, 0.08, 4.00)),
]


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class RequestUsage:
    key: str
    request_id: str
    message_id: str
    timestamp_raw: Optional[str]
    timestamp: Optional[datetime]
    model: str
    model_label: Optional[str]

    input_tokens: int
    cache_read_tokens: int
    cache_5m_tokens: int
    cache_1h_tokens: int
    output_tokens: int

    cost_input: Optional[float]
    cost_cache_read: Optional[float]
    cost_cache_5m: Optional[float]
    cost_cache_1h: Optional[float]
    cost_output: Optional[float]
    total_cost: Optional[float]

    project_id: str
    project_name: str
    project_cwd: Optional[str]
    session: str
    source_file: Path
    line_no: int


@dataclass
class SessionMeta:
    project_id: str
    project_name: str
    project_cwd: Optional[str]
    session: str
    started_at_raw: Optional[str] = None
    started_at: Optional[datetime] = None
    first_prompt: Optional[str] = None
    source_file: Optional[Path] = None
    line_no: Optional[int] = None


@dataclass
class ScanStats:
    jsonl_files: int = 0
    invalid_json_lines: int = 0
    duplicate_usage_rows: int = 0
    synthetic_rows: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def parse_timestamp(value) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def localize(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    try:
        if dt.tzinfo is not None:
            return dt.astimezone()
        return dt
    except (ValueError, OSError):
        return dt


def timestamp_string(dt: Optional[datetime], raw: Optional[str], *, time_only: bool = False) -> str:
    dt = localize(dt)
    if dt is None:
        return raw or "-"
    try:
        return dt.strftime("%H:%M:%S" if time_only else "%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return raw or "-"


def resolve_price(model: str) -> tuple[Optional[str], Optional[Price]]:
    model = (model or "").strip()
    for rule in PRICE_RULES:
        if rule.pattern.match(model):
            return rule.label, rule.price
    return None, None


def normalize_prompt_text(text: str) -> str:
    return " ".join(str(text).replace("\x00", "").split())


def extract_user_prompt(row: dict) -> Optional[str]:
    """
    Extract a human/user-facing prompt from a Claude Code transcript row.

    Claude Code can store tool results as type=user, so tool_result content is
    excluded. A known automatic continuation meta-prompt is also excluded.
    """
    if row.get("type") != "user":
        return None

    if row.get("toolUseResult") is not None:
        return None

    message = row.get("message") or {}
    content = message.get("content")

    texts: list[str] = []
    saw_tool_result = False

    if isinstance(content, str):
        if content.strip():
            texts.append(content)
    elif isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type == "tool_result":
                saw_tool_result = True
                continue
            if item_type == "text":
                value = item.get("text")
                if isinstance(value, str) and value.strip():
                    texts.append(value)

    if not texts:
        return None

    # Claude Code tool-result carriers are transcript plumbing, not a user's
    # session-identifying prompt.
    if saw_tool_result:
        return None

    prompt = normalize_prompt_text(" ".join(texts))
    if not prompt:
        return None

    if row.get("isMeta") is True and prompt == "Continue from where you left off.":
        return None

    return prompt


def friendly_project_name(cwd: Optional[str], project_id: str) -> str:
    if not cwd:
        return project_id

    try:
        raw = str(cwd).rstrip("/\\")
        if "\\" in raw:
            name = PureWindowsPath(raw).name
        else:
            name = PurePosixPath(raw).name
        return name or project_id
    except Exception:
        return project_id


def short_session(session: str, width: int = 12) -> str:
    if len(session) <= width:
        return session
    return session[:width] + "…"


def money(value: Optional[float], digits: int = 4) -> str:
    return "N/A" if value is None else f"${value:.{digits}f}"


def truncate(text: Optional[str], width: int) -> str:
    if not text:
        return "(prompt not found)"
    if width == 0 or len(text) <= width:
        return text
    if width <= 1:
        return "…"
    return text[: width - 1] + "…"


def project_root() -> Path:
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(config).expanduser() if config else Path.home() / ".claude"
    return base / "projects"


def encode_project_path(path: Path) -> str:
    absolute = str(path.expanduser().resolve())
    return re.sub(r"[^A-Za-z0-9]", "-", absolute)


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def iter_jsonl_files(directory: Path) -> Iterable[Path]:
    for file in directory.rglob("*.jsonl"):
        if file.is_file():
            yield file


def session_name_from_file(file: Path, project_dir: Path) -> str:
    """
    Main transcript:
        <project>/<session-id>.jsonl

    Subagent transcript:
        <project>/<session-id>/subagents/agent-....jsonl

    Nested JSONL is attributed to its parent session directory.
    """
    try:
        rel = file.relative_to(project_dir)
    except ValueError:
        return file.stem

    if len(rel.parts) == 1:
        return file.stem
    return rel.parts[0]


def is_main_session_file(file: Path, project_dir: Path, session: str) -> bool:
    try:
        rel = file.relative_to(project_dir)
        return len(rel.parts) == 1 and file.stem == session
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Target discovery
# ---------------------------------------------------------------------------

def collect_targets(args) -> tuple[list[tuple[Path, Path]], str]:
    root = project_root()

    if args.file:
        file = Path(args.file).expanduser().resolve()
        if not file.is_file():
            raise FileNotFoundError(f"JSONL file not found: {file}")

        project_dir = file.parent
        if root.exists() and is_inside(file, root):
            rel = file.relative_to(root.resolve())
            if rel.parts:
                project_dir = root / rel.parts[0]
        return [(file, project_dir)], f"file: {file}"

    if args.log_dir:
        project_dir = Path(args.log_dir).expanduser().resolve()
        if not project_dir.is_dir():
            raise FileNotFoundError(f"log directory not found: {project_dir}")
        files = [(f, project_dir) for f in iter_jsonl_files(project_dir)]
        return files, f"log-dir: {project_dir}"

    if args.project:
        supplied = Path(args.project).expanduser().resolve()

        # Accept the real repository/work directory OR its Claude log directory.
        if root.exists() and supplied.is_dir() and is_inside(supplied, root):
            rel = supplied.relative_to(root.resolve())
            if not rel.parts:
                raise FileNotFoundError(
                    "--project points to the projects root. Use --all-projects."
                )
            project_dir = root / rel.parts[0]
        else:
            project_dir = root / encode_project_path(supplied)

        if not project_dir.is_dir():
            raise FileNotFoundError(
                "Claude log directory not found for project:\n"
                f"  supplied: {supplied}\n"
                f"  expected: {project_dir}"
            )

        files = [(f, project_dir) for f in iter_jsonl_files(project_dir)]
        return files, f"project logs: {project_dir}"

    # Default (and explicit --all-projects): scan everything.
    if not root.is_dir():
        raise FileNotFoundError(f"Claude projects directory not found: {root}")

    pairs: list[tuple[Path, Path]] = []
    for project_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        pairs.extend((f, project_dir) for f in iter_jsonl_files(project_dir))

    return pairs, f"all projects: {root}"


# ---------------------------------------------------------------------------
# Transcript scanning
# ---------------------------------------------------------------------------

def scan_logs(
    files_with_context: Iterable[tuple[Path, Path]],
) -> tuple[list[RequestUsage], dict[tuple[str, str], SessionMeta], ScanStats]:
    requests: dict[str, RequestUsage] = {}
    sessions: dict[tuple[str, str], SessionMeta] = {}
    stats = ScanStats()

    targets = list(files_with_context)
    stats.jsonl_files = len({f for f, _ in targets})

    # Keep the best-known cwd/name for each encoded project.
    project_info: dict[str, tuple[Optional[str], str]] = {}

    for file, project_dir in targets:
        project_id = project_dir.name
        session = session_name_from_file(file, project_dir)
        session_key = (project_id, session)
        main_file = is_main_session_file(file, project_dir, session)

        try:
            fh = file.open(encoding="utf-8")
        except OSError as exc:
            print(f"WARNING: cannot read {file}: {exc}", file=sys.stderr)
            continue

        with fh:
            for line_no, line in enumerate(fh, start=1):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    stats.invalid_json_lines += 1
                    continue

                cwd = row.get("cwd")
                if isinstance(cwd, str) and cwd.strip():
                    current = project_info.get(project_id)
                    friendly = friendly_project_name(cwd, project_id)
                    if current is None or current[0] is None:
                        project_info[project_id] = (cwd, friendly)

                project_cwd, project_name = project_info.get(
                    project_id, (None, project_id)
                )

                # First real user prompt, preferring the main session transcript
                # over a nested subagent transcript.
                prompt = extract_user_prompt(row)
                if prompt is not None:
                    existing = sessions.get(session_key)
                    should_take = existing is None

                    if existing is not None and main_file:
                        old_main = (
                            existing.source_file is not None
                            and is_main_session_file(
                                existing.source_file, project_dir, session
                            )
                        )
                        should_take = not old_main

                    if should_take:
                        ts_raw = row.get("timestamp")
                        sessions[session_key] = SessionMeta(
                            project_id=project_id,
                            project_name=project_name,
                            project_cwd=project_cwd,
                            session=session,
                            started_at_raw=ts_raw,
                            started_at=parse_timestamp(ts_raw),
                            first_prompt=prompt,
                            source_file=file,
                            line_no=line_no,
                        )

                if row.get("type") != "assistant":
                    continue

                message = row.get("message") or {}
                usage = message.get("usage")
                if not isinstance(usage, dict):
                    continue

                model = str(message.get("model") or "unknown")
                if model == "<synthetic>":
                    stats.synthetic_rows += 1
                    continue

                request_id = str(row.get("requestId") or "")
                message_id = str(message.get("id") or "")

                # Dedupe is scoped to project/session. Claude Code can write the
                # same API response into multiple transcript rows/files.
                scope = f"{project_id}/{session}"
                if request_id:
                    key = f"{scope}:request:{request_id}"
                elif message_id:
                    key = f"{scope}:message:{message_id}"
                else:
                    key = f"{scope}:line:{file.resolve()}:{line_no}"

                if key in requests:
                    stats.duplicate_usage_rows += 1
                    continue

                input_tokens = to_int(usage.get("input_tokens"))
                cache_read_tokens = to_int(usage.get("cache_read_input_tokens"))
                output_tokens = to_int(usage.get("output_tokens"))

                cache_creation = usage.get("cache_creation") or {}
                cache_5m_tokens = to_int(
                    cache_creation.get("ephemeral_5m_input_tokens")
                )
                cache_1h_tokens = to_int(
                    cache_creation.get("ephemeral_1h_input_tokens")
                )

                # Compatibility fallback for logs that expose only aggregate
                # cache_creation_input_tokens.
                if cache_5m_tokens == 0 and cache_1h_tokens == 0:
                    cache_5m_tokens = to_int(
                        usage.get("cache_creation_input_tokens")
                    )

                model_label, price = resolve_price(model)

                if price is None:
                    ci = ccr = cc5 = cc1 = co = total = None
                else:
                    ci = input_tokens / 1_000_000 * price.input
                    ccr = cache_read_tokens / 1_000_000 * price.cache_read
                    cc5 = cache_5m_tokens / 1_000_000 * price.cache_5m
                    cc1 = cache_1h_tokens / 1_000_000 * price.cache_1h
                    co = output_tokens / 1_000_000 * price.output
                    total = ci + ccr + cc5 + cc1 + co

                ts_raw = row.get("timestamp")
                requests[key] = RequestUsage(
                    key=key,
                    request_id=request_id,
                    message_id=message_id,
                    timestamp_raw=ts_raw,
                    timestamp=parse_timestamp(ts_raw),
                    model=model,
                    model_label=model_label,
                    input_tokens=input_tokens,
                    cache_read_tokens=cache_read_tokens,
                    cache_5m_tokens=cache_5m_tokens,
                    cache_1h_tokens=cache_1h_tokens,
                    output_tokens=output_tokens,
                    cost_input=ci,
                    cost_cache_read=ccr,
                    cost_cache_5m=cc5,
                    cost_cache_1h=cc1,
                    cost_output=co,
                    total_cost=total,
                    project_id=project_id,
                    project_name=project_name,
                    project_cwd=project_cwd,
                    session=session,
                    source_file=file,
                    line_no=line_no,
                )

    # A project cwd may be discovered after earlier requests/session metadata.
    # Normalize names once scanning is complete.
    for r in requests.values():
        cwd, name = project_info.get(r.project_id, (r.project_cwd, r.project_name))
        r.project_cwd = cwd
        r.project_name = name

    for s in sessions.values():
        cwd, name = project_info.get(s.project_id, (s.project_cwd, s.project_name))
        s.project_cwd = cwd
        s.project_name = name

    return list(requests.values()), sessions, stats


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def apply_period_filter(rows: list[RequestUsage], args) -> list[RequestUsage]:
    if args.all_time:
        return rows

    now = datetime.now().astimezone()

    if args.days is not None:
        cutoff = now - timedelta(days=args.days)

        def keep_days(r: RequestUsage) -> bool:
            dt = localize(r.timestamp)
            if dt is None:
                return False
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=now.tzinfo)
            return dt >= cutoff

        return [r for r in rows if keep_days(r)]

    # Default: today, in the machine's local timezone.
    today = now.date()

    def keep_today(r: RequestUsage) -> bool:
        dt = localize(r.timestamp)
        return dt is not None and dt.date() == today

    return [r for r in rows if keep_today(r)]


def apply_session_filter(
    rows: list[RequestUsage], session_filter: Optional[str]
) -> list[RequestUsage]:
    if not session_filter:
        return rows
    needle = session_filter.lower()
    return [r for r in rows if needle in r.session.lower()]


# ---------------------------------------------------------------------------
# Aggregation / output
# ---------------------------------------------------------------------------

def sum_cost(rows: Iterable[RequestUsage], attr: str) -> float:
    return sum((getattr(r, attr) or 0.0) for r in rows)


def summarize_cost(rows: list[RequestUsage]) -> dict[str, float]:
    known = [r for r in rows if r.total_cost is not None]
    return {
        "input": sum_cost(known, "cost_input"),
        "cache_read": sum_cost(known, "cost_cache_read"),
        "cache_5m": sum_cost(known, "cost_cache_5m"),
        "cache_1h": sum_cost(known, "cost_cache_1h"),
        "cache_write": (
            sum_cost(known, "cost_cache_5m")
            + sum_cost(known, "cost_cache_1h")
        ),
        "output": sum_cost(known, "cost_output"),
        "total": sum_cost(known, "total_cost"),
    }


def request_sort_key(r: RequestUsage):
    dt = localize(r.timestamp)
    if dt is None:
        return (1, 0.0, str(r.source_file), r.line_no)
    try:
        return (0, dt.timestamp(), str(r.source_file), r.line_no)
    except (ValueError, OSError):
        return (1, 0.0, str(r.source_file), r.line_no)


def period_label(args) -> str:
    if args.all_time:
        return "all available local history"
    if args.days is not None:
        return f"last {args.days} x 24 hours"
    return "today (local time)"


def print_overview(rows: list[RequestUsage], stats: ScanStats, args) -> None:
    known = [r for r in rows if r.total_cost is not None]
    unknown = [r for r in rows if r.total_cost is None]
    costs = summarize_cost(rows)

    print("Claude Code Cost Estimate")
    print(f"Period             : {period_label(args)}")
    print(f"Estimated API cost : ${costs['total']:.4f}")
    print(f"API requests       : {len(rows):,}")
    print()

    print("Cost breakdown")
    print(f"  input        : ${costs['input']:.4f}")
    print(f"  cache-read   : ${costs['cache_read']:.4f}")
    print(
        f"  cache-write  : ${costs['cache_write']:.4f} "
        f"(5m ${costs['cache_5m']:.4f} / 1h ${costs['cache_1h']:.4f})"
    )
    print(f"  output       : ${costs['output']:.4f}")

    if known:
        print(f"  avg/request  : ${costs['total'] / len(known):.4f}")

    if unknown:
        models = sorted({r.model for r in unknown})
        print()
        print(
            f"WARNING: {len(unknown)} request(s) excluded from the dollar total "
            "because pricing is unknown:"
        )
        for model in models:
            print(f"  - {model}")

    if args.verbose:
        print()
        print("Scan diagnostics")
        print(f"  JSONL files      : {stats.jsonl_files:,}")
        print(f"  deduped rows     : {stats.duplicate_usage_rows:,}")
        print(f"  synthetic rows   : {stats.synthetic_rows:,}")
        print(f"  invalid JSON     : {stats.invalid_json_lines:,}")
        print()
        print("Token totals")
        print(f"  input            : {sum(r.input_tokens for r in rows):,}")
        print(f"  cache-read       : {sum(r.cache_read_tokens for r in rows):,}")
        print(f"  cache-write 5m   : {sum(r.cache_5m_tokens for r in rows):,}")
        print(f"  cache-write 1h   : {sum(r.cache_1h_tokens for r in rows):,}")
        print(f"  output           : {sum(r.output_tokens for r in rows):,}")


def grouped(rows: list[RequestUsage], key_func):
    result = defaultdict(lambda: {"requests": 0, "cost": 0.0, "unknown": 0})
    for r in rows:
        key = key_func(r)
        result[key]["requests"] += 1
        if r.total_cost is None:
            result[key]["unknown"] += 1
        else:
            result[key]["cost"] += r.total_cost
    return result


def print_group(title: str, rows: list[RequestUsage], key_func, display_func=None) -> None:
    groups = grouped(rows, key_func)
    if not groups:
        return

    items = sorted(groups.items(), key=lambda kv: kv[1]["cost"], reverse=True)

    print()
    print(f"=== {title} ===")
    print(f"{'cost':>11}  {'requests':>8}  name")
    print("-" * 72)

    for key, info in items:
        name = display_func(key) if display_func else str(key)
        unknown_suffix = (
            f"  [unknown cost: {info['unknown']} req]"
            if info["unknown"]
            else ""
        )
        print(
            f"${info['cost']:>10.4f}  "
            f"{info['requests']:>8}  "
            f"{name}{unknown_suffix}"
        )


def session_groups(rows: list[RequestUsage]):
    data = defaultdict(list)
    for r in rows:
        data[(r.project_id, r.session)].append(r)
    return data


def print_top_sessions(
    rows: list[RequestUsage],
    session_meta: dict[tuple[str, str], SessionMeta],
    limit: int,
    prompt_width: int,
) -> None:
    groups = session_groups(rows)
    if not groups:
        return

    ranked = []
    for key, group_rows in groups.items():
        costs = summarize_cost(group_rows)
        ranked.append((key, group_rows, costs))

    ranked.sort(key=lambda item: item[2]["total"], reverse=True)
    total_sessions = len(ranked)

    if limit > 0:
        ranked = ranked[:limit]

    title = (
        f"Top sessions ({len(ranked)} of {total_sessions})"
        if limit > 0
        else f"All sessions ({total_sessions})"
    )
    print()
    print(f"=== {title} ===")

    for (project_id, session), group_rows, costs in ranked:
        first = group_rows[0]
        meta = session_meta.get((project_id, session))
        started = (
            timestamp_string(meta.started_at, meta.started_at_raw)
            if meta
            else "-"
        )
        prompt = truncate(meta.first_prompt if meta else None, prompt_width)

        print()
        print(
            f"${costs['total']:.4f}  "
            f"{len(group_rows)} req  "
            f"started {started}"
        )
        print(f"  {first.project_name} / {short_session(session)}")
        print(
            "  cost: "
            f"input ${costs['input']:.4f} | "
            f"cache-read ${costs['cache_read']:.4f} | "
            f"cache-write ${costs['cache_write']:.4f} | "
            f"output ${costs['output']:.4f}"
        )
        print(f"  prompt: {prompt}")

        if any(r.total_cost is None for r in group_rows):
            print("  warning: some requests have unknown model pricing")

    if limit > 0 and total_sessions > limit:
        print()
        print(
            f"... {total_sessions - limit} more session(s); "
            "use --top-sessions 0 to show all."
        )


def print_top_requests(rows: list[RequestUsage], count: int) -> None:
    if count <= 0:
        return

    priced = [r for r in rows if r.total_cost is not None]
    ranked = sorted(
        priced, key=lambda r: r.total_cost or 0.0, reverse=True
    )[:count]

    if not ranked:
        return

    print()
    print(f"=== Most expensive API requests (top {len(ranked)}) ===")

    for r in ranked:
        cache_write = (r.cost_cache_5m or 0.0) + (r.cost_cache_1h or 0.0)
        print()
        print(
            f"{timestamp_string(r.timestamp, r.timestamp_raw)}  "
            f"{money(r.total_cost)}  {r.model_label or r.model}"
        )
        print(f"  {r.project_name} / {short_session(r.session)}")
        print(
            "  cost: "
            f"input {money(r.cost_input)} | "
            f"cache-read {money(r.cost_cache_read)} | "
            f"cache-write ${cache_write:.4f} | "
            f"output {money(r.cost_output)}"
        )
        print(
            f"  cache-read tokens: {r.cache_read_tokens:,}"
        )


def print_timeline(rows: list[RequestUsage]) -> None:
    if not rows:
        return

    print()
    print("=== Timeline (API requests) ===")

    for r in sorted(rows, key=request_sort_key):
        cache_write = (r.cost_cache_5m or 0.0) + (r.cost_cache_1h or 0.0)
        print()
        print(
            f"{timestamp_string(r.timestamp, r.timestamp_raw, time_only=True)}  "
            f"{money(r.total_cost)}  "
            f"{r.model_label or r.model}"
        )
        print(f"  {r.project_name} / {short_session(r.session)}")
        print(
            "  cost: "
            f"input {money(r.cost_input)} | "
            f"cache-read {money(r.cost_cache_read)} | "
            f"cache-write ${cache_write:.4f} | "
            f"output {money(r.cost_output)}"
        )
        print(f"  cache-read tokens: {r.cache_read_tokens:,}")


def print_footer() -> None:
    print()
    print(
        "NOTE: API-equivalent estimate only. Embedded standard first-party "
        f"Claude API pricing was checked {PRICING_CHECKED}."
    )
    print(
        "Not included: fast mode, data-residency multipliers, server-side tool "
        "charges, cloud-provider pricing, negotiated discounts, taxes, and "
        "other non-token charges."
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate Claude Code API-equivalent cost from local JSONL transcripts. "
            "With no arguments, scans all ~/.claude/projects and shows today's "
            "usage plus the top 10 sessions."
        )
    )

    target = parser.add_mutually_exclusive_group()
    target.add_argument("--file", help="Analyze one JSONL transcript file.")
    target.add_argument(
        "--log-dir",
        help="Analyze all JSONL recursively under one Claude project log directory.",
    )
    target.add_argument(
        "--project",
        help=(
            "Analyze one project. Accepts a repository/work directory or its "
            "~/.claude/projects/<project> log directory."
        ),
    )
    target.add_argument(
        "--all-projects",
        action="store_true",
        help="Scan all ~/.claude/projects (this is the default).",
    )

    period = parser.add_mutually_exclusive_group()
    period.add_argument(
        "--today",
        action="store_true",
        help="Analyze today in local time (this is the default).",
    )
    period.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Analyze the last N x 24 hours.",
    )
    period.add_argument(
        "--all-time",
        action="store_true",
        help="Analyze all available local transcript history.",
    )

    parser.add_argument(
        "--session",
        help="Only include session IDs containing this text.",
    )
    parser.add_argument(
        "--top-sessions",
        "--session-limit",
        dest="top_sessions",
        type=int,
        default=10,
        metavar="N",
        help="Show top N sessions by cost (default 10; 0 = all).",
    )
    parser.add_argument(
        "--prompt-width",
        type=int,
        default=100,
        metavar="N",
        help="First user prompt preview width (default 100; 0 = full).",
    )
    parser.add_argument(
        "--timeline",
        action="store_true",
        help="Append request-by-request chronological cost history.",
    )
    parser.add_argument(
        "--top-requests",
        type=int,
        default=0,
        metavar="N",
        help="Append the N most expensive individual API requests.",
    )
    parser.add_argument(
        "--no-sessions",
        action="store_true",
        help="Do not print the session ranking.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show scan, dedupe, and token diagnostics.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.days is not None and args.days <= 0:
        parser.error("--days must be >= 1")
    if args.top_sessions < 0:
        parser.error("--top-sessions must be >= 0")
    if args.top_requests < 0:
        parser.error("--top-requests must be >= 0")
    if args.prompt_width < 0:
        parser.error("--prompt-width must be >= 0")

    try:
        targets, target_description = collect_targets(args)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not targets:
        print("ERROR: no JSONL files found.", file=sys.stderr)
        return 2

    rows, session_meta, stats = scan_logs(targets)
    rows = apply_period_filter(rows, args)
    rows = apply_session_filter(rows, args.session)

    if args.verbose:
        print(f"Target             : {target_description}")
        print(f"Pricing checked    : {PRICING_CHECKED}")
        print()

    print_overview(rows, stats, args)

    # Use stable IDs for grouping; display the friendly project name.
    project_names: dict[str, str] = {}
    for r in rows:
        project_names[r.project_id] = r.project_name

    print_group(
        "By project",
        rows,
        lambda r: r.project_id,
        lambda project_id: project_names.get(project_id, project_id),
    )

    print_group(
        "By model",
        rows,
        lambda r: r.model_label or f"UNKNOWN: {r.model}",
    )

    if not args.no_sessions:
        print_top_sessions(
            rows,
            session_meta,
            limit=args.top_sessions,
            prompt_width=args.prompt_width,
        )

    print_top_requests(rows, args.top_requests)

    if args.timeline:
        print_timeline(rows)

    print_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

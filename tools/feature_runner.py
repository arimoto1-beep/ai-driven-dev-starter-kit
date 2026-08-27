#!/usr/bin/env python3
"""feature オートモードの薄い runner。

Worker（prompts/run_stage.md）と Reviewer（prompts/review_stage.md）を
別プロセスとして交互に起動し、Gate記録の front matter を読んで状態遷移する。

このスクリプトはプロジェクト固有の知識を持たない。
stage 名、成果物、モデル、起動コマンドは、すべて
docs/rules/project/70_feature_loop.md の設定ブロックから読む。

標準ライブラリのみを使用する。
"""
import argparse
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CONFIG_DOC = "docs/rules/project/70_feature_loop.md"
CONFIG_FENCE = "feature_loop"
LOCAL_OVERRIDE = "tools/feature_loop.local"

WORKER_PROMPT = "prompts/run_stage.md"
REVIEWER_PROMPT = "prompts/review_stage.md"

TERMINAL_VERDICTS = {"PASS", "RETURN", "BLOCKED"}
PLACEHOLDER_RE = re.compile(r"^<.*>$")


# ---------------------------------------------------------------- 基本ユーティリティ


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def now() -> datetime:
    return datetime.now().astimezone()


def timestamp() -> str:
    return now().strftime("%Y%m%dT%H%M%S")


def is_placeholder(value: str) -> bool:
    """`<記入してください>` のような未設定値かどうか。"""
    return not value or bool(PLACEHOLDER_RE.match(value.strip()))


def split_list(value: str) -> list[str]:
    """カンマ区切りの値をリストにする。空要素は落とす。"""
    return [item.strip() for item in value.split(",") if item.strip()]


# ---------------------------------------------------------------- フラットな key: value


def parse_flat(text: str, sep: str) -> dict[str, str]:
    """1行1件の `key<sep>value` を読む。

    入れ子とリスト構文は扱わない。値の中の sep は分割しない（最初の1つだけで分ける）。
    `#` で始まる行はコメント。
    """
    result: dict[str, str] = {}

    for raw in text.splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if sep not in line:
            continue

        key, _, value = line.partition(sep)
        key = key.strip()

        if not key:
            continue

        result[key] = value.strip()

    return result


def extract_fenced_block(text: str, language: str) -> str:
    """```<language> ... ``` の中身を返す。見つからなければ空文字。"""
    pattern = rf"^```{re.escape(language)}\s*$(.*?)^```\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def read_config(root: Path) -> dict[str, str]:
    """70_feature_loop.md の設定ブロックを読み、ローカル上書きを適用する。"""
    doc = root / CONFIG_DOC

    if not doc.exists():
        raise SystemExit(f"設定ファイルが見つかりません: {CONFIG_DOC}")

    block = extract_fenced_block(doc.read_text(encoding="utf-8"), CONFIG_FENCE)

    if not block.strip():
        raise SystemExit(
            f"{CONFIG_DOC} に ```{CONFIG_FENCE} ブロックがありません。"
        )

    config = parse_flat(block, "=")

    local = root / LOCAL_OVERRIDE
    if local.exists():
        config.update(parse_flat(local.read_text(encoding="utf-8"), "="))

    return config


def read_front_matter(path: Path) -> dict[str, str]:
    """Markdown 先頭の `---` で囲まれた front matter を読む。

    フラットな `key: value` だけを扱う。本文は読まない。
    """
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, flags=re.DOTALL)

    if not match:
        return {}

    return parse_flat(match.group(1), ":")


# ---------------------------------------------------------------- Gate記録


def gates_dir(root: Path, feature_dir: str) -> Path:
    return root / feature_dir / "gates"


def list_records(root: Path, feature_dir: str) -> list[Path]:
    """Gate記録を名前順（= 実行順）で返す。連番プレフィックスが順序を保証する。"""
    directory = gates_dir(root, feature_dir)

    if not directory.exists():
        return []

    return sorted(p for p in directory.glob("*.md") if p.is_file())


def latest_record(root: Path, feature_dir: str) -> Path | None:
    """全stage横断で最新の1件。

    stage 別に最新を取ると、RETURN の直後に差し戻し前の古い PASS を
    採用してしまう。因果を正しく追うため、横断で最新を見る。
    """
    records = list_records(root, feature_dir)
    return records[-1] if records else None


def next_seq(root: Path, feature_dir: str) -> int:
    records = list_records(root, feature_dir)
    max_seq = 0

    for path in records:
        head = path.name.split("_", 1)[0]
        if head.isdigit():
            max_seq = max(max_seq, int(head))

    return max_seq + 1


def new_record_path(root: Path, feature_dir: str, stage: str) -> Path:
    """既存ファイルを上書きしない名前を返す。"""
    directory = gates_dir(root, feature_dir)
    base = f"{next_seq(root, feature_dir):04d}_{timestamp()}_{stage.lower()}"

    candidate = directory / f"{base}.md"
    suffix = 2

    while candidate.exists():
        candidate = directory / f"{base}_{suffix}.md"
        suffix += 1

    return candidate


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


# ---------------------------------------------------------------- 人間確認欄


def section_body(text: str, heading: str) -> str:
    """`### <heading>` 配下を、次の同レベル以上の見出しまで取得する。"""
    pattern = rf"^#{{2,3}}\s*{re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)

    if not match:
        return ""

    start = match.end()
    nxt = re.search(r"^#{1,3} .+$", text[start:], flags=re.MULTILINE)

    return text[start:] if not nxt else text[start : start + nxt.start()]


def is_approved(record: Path, heading: str) -> bool:
    """承認セクションのチェックボックスが全て `[x]` かどうか。

    「判断してほしいこと」の選択肢は排他なので未チェックが残る。
    そのため承認セクションだけを見る。
    """
    if not heading:
        return False

    body = section_body(record.read_text(encoding="utf-8"), heading)

    if not body.strip():
        return False

    boxes = re.findall(r"^\s*-\s*\[([ xX])\]", body, flags=re.MULTILINE)

    return bool(boxes) and all(box.lower() == "x" for box in boxes)


def file_hash(path: Path) -> str:
    """ファイル内容の SHA-256。仕様 baseline の同一性判定に使う。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_human_note(record: Path, heading: str) -> str:
    """「気になる点」のフェンス内の自然文を返す。"""
    if not heading:
        return ""

    body = section_body(record.read_text(encoding="utf-8"), heading)
    match = re.search(r"^```\w*\s*$(.*?)^```\s*$", body, flags=re.MULTILINE | re.DOTALL)

    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------- 変更範囲のガード


def git_files(root: Path) -> list[str]:
    """追跡ファイルと、無視されていない未追跡ファイルの一覧。"""
    paths: list[str] = []

    for args in (
        ["git", "ls-files", "-z"],
        ["git", "ls-files", "-z", "--others", "--exclude-standard"],
    ):
        out = subprocess.run(args, cwd=root, capture_output=True, text=True)

        if out.returncode != 0:
            continue

        paths.extend(item for item in out.stdout.split("\0") if item)

    return paths


def snapshot(root: Path) -> dict[str, str]:
    """パス -> 内容ハッシュ。

    内容ハッシュで比較するため、実行前から未コミット変更があったファイルへの
    「さらなる変更」も検出できる。git status のパス集合だけでは検出できない。
    """
    result: dict[str, str] = {}

    for name in git_files(root):
        path = root / name

        try:
            if not path.is_file():
                continue
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            result[name] = "unreadable"

    return result


def diff_snapshots(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """2つのスナップショットの間で発生した変更（追加・更新・削除）を返す。"""
    changed = {
        name for name in after if before.get(name) != after[name]
    } | {
        name for name in before if name not in after
    }

    return sorted(changed)


def expand(patterns: str, ctx: dict[str, str]) -> list[str]:
    """設定値のプレースホルダを展開し、リストにする。"""
    expanded = patterns
    for key, value in ctx.items():
        expanded = expanded.replace("{" + key + "}", value)

    return split_list(expanded)


def is_allowed(path: str, allowed: list[str]) -> bool:
    """末尾が `/` のパターンはディレクトリ前方一致、それ以外は完全一致。"""
    for pattern in allowed:
        if pattern.endswith("/"):
            if path.startswith(pattern):
                return True
        elif path == pattern:
            return True

    return False


def check_guard(changed: list[str], allowed: list[str]) -> list[str]:
    return [path for path in changed if not is_allowed(path, allowed)]


# ---------------------------------------------------------------- 仕様 baseline


def spec_stage(config: dict[str, str]) -> str:
    return config.get("spec_stage", "")


def spec_path(root: Path, config: dict[str, str], ctx: dict[str, str]) -> Path | None:
    patterns = expand(config.get("spec_artifact", ""), ctx)
    return root / patterns[0] if patterns else None


def is_manufacturing_stage(config: dict[str, str], stage: str) -> bool:
    """仕様 stage より後の stage は、すべて製造 stage。"""
    stages = split_list(config.get("stages", ""))
    target = spec_stage(config)

    if not target or target not in stages or stage not in stages:
        return False

    return stages.index(stage) > stages.index(target)


def find_spec_approval(root: Path, config: dict[str, str],
                       feature_dir: str,
                       required_spec_hash: str | None = None,
                       ) -> tuple[Path | None, dict[str, str]]:
    """人間が承認済みの仕様 stage 記録を、新しい順に探す。

    ``required_spec_hash`` が指定された場合は、その baseline と一致する承認だけを
    対象にする。承認は「どの 20_spec.md を承認したか」を表すため、最新の記録で
    ある必要はない。内容が一致する承認が1件あればよい。
    """
    stage = spec_stage(config)
    heading = config.get(f"approval_heading_{stage.lower()}", "")

    if not stage or not heading:
        return None, {}

    for path in reversed(list_records(root, feature_dir)):
        front = read_front_matter(path)

        if front.get("gate") != stage or front.get("verdict") != "PASS":
            continue

        if not is_approved(path, heading):
            continue

        if required_spec_hash is not None and front.get("spec_hash", "") != required_spec_hash:
            continue

        return path, front

    return None, {}


def check_spec_baseline(root: Path, config: dict[str, str],
                        ctx: dict[str, str]) -> tuple[bool, str]:
    """製造開始条件（Manufacturing Preflight）を確認する。

    - 仕様レビューが PASS していること
    - 人間の仕様承認があること
    - 承認対象の 20_spec.md と現在の 20_spec.md が同一 baseline であること
    """
    target = spec_path(root, config, ctx)

    if target is None:
        return False, "設定に spec_artifact がありません。"

    if not target.exists():
        return False, f"仕様書が見つかりません: {rel(root, target)}"

    current = file_hash(target)
    record, _ = find_spec_approval(
        root, config, ctx["feature_dir"], required_spec_hash=current,
    )

    if record is not None:
        return True, ""

    # 一致する承認が無い場合だけ、最新の承認済み記録を診断用に確認する。
    # これにより A承認 → B承認 → Aへ戻す、のような場合でも過去のA承認を
    # 正しく利用できる一方、現在の baseline が未承認なら安全側に停止できる。
    latest_approval, front = find_spec_approval(root, config, ctx["feature_dir"])

    if latest_approval is None:
        return False, (
            f"{spec_stage(config)} の人間による仕様承認がありません。\n"
            "仕様をレビューし、Gate記録の承認欄にチェックを入れてから製造を開始してください。"
        )

    approved = front.get("spec_hash", "")

    if not approved:
        return False, (
            f"承認記録に spec_hash がありません: {rel(root, latest_approval)}\n"
            "仕様レビューを実行し直して、承認し直してください。"
        )

    return False, (
        "現在の仕様書に一致する人間承認済み baseline がありません。\n"
        f"  最新の承認記録: {rel(root, latest_approval)}\n"
        f"  承認時: {approved[:12]}\n"
        f"  現在  : {current[:12]}\n"
        "現在の仕様をレビューし、承認してから製造を開始してください。"
    )


# ---------------------------------------------------------------- stage 成果物の baseline


def stage_artifacts(config: dict[str, str], stage: str, ctx: dict[str, str]) -> list[str]:
    """その stage が baseline 化する成果物のパターン。"""
    return expand(config.get(f"stage_{stage.lower()}_artifacts", ""), ctx)


def hash_paths(root: Path, patterns: list[str]) -> str:
    """複数ファイルをまとめた内容ハッシュ。

    パス名も混ぜるため、内容の変更だけでなく追加・削除・改名も検出できる。
    ディレクトリ指定は git が見ているファイルだけを対象にする
    （`__pycache__` のような無視対象を数えない）。
    """
    if not patterns:
        return ""

    names = {name for name in git_files(root) if is_allowed(name, patterns)}

    # 作成直後で git がまだ見ていない明示指定ファイルも拾う
    names.update(
        pattern for pattern in patterns
        if not pattern.endswith("/") and (root / pattern).is_file()
    )

    digest = hashlib.sha256()

    for name in sorted(names):
        digest.update(name.encode("utf-8") + b"\0")

        try:
            digest.update((root / name).read_bytes())
        except OSError:
            digest.update(b"<unreadable>")

        digest.update(b"\0")

    return digest.hexdigest()


def current_artifacts_hash(root: Path, config: dict[str, str], ctx: dict[str, str],
                           stage: str) -> str:
    """その stage の成果物の、現在の内容ハッシュ。

    `spec_hash` と同じ考え方で、runner が計算して Reviewer へ渡し、
    runner が後で再計算して照合する。AIの計算には依存しない。
    """
    return hash_paths(root, stage_artifacts(config, stage, ctx))


def latest_pass_of_stage(root: Path, feature_dir: str, stage: str) -> Path | None:
    for path in reversed(list_records(root, feature_dir)):
        front = read_front_matter(path)
        if front.get("gate") == stage and front.get("verdict") == "PASS":
            return path

    return None


def stage_baseline_state(root: Path, config: dict[str, str], ctx: dict[str, str],
                         stage: str) -> str:
    """その stage の成果物が、PASS 当時から変わっていないか。

    戻り値:
      no_pass  まだ PASS 記録がない
      unknown  判定材料がない（設定なし、または記録に artifacts_hash がない）
      match    PASS 当時と同じ
      changed  PASS 後に変更されている
    """
    if not stage_artifacts(config, stage, ctx):
        return "unknown"

    record = latest_pass_of_stage(root, ctx["feature_dir"], stage)

    if record is None:
        return "no_pass"

    recorded = read_front_matter(record).get("artifacts_hash", "")

    # artifacts_hash を持たない過去の記録は判定できない。安全側に倒すと
    # 既存 feature がすべて停止するため、判定不能として扱い停止しない。
    if not recorded:
        return "unknown"

    return "match" if recorded == current_artifacts_hash(root, config, ctx, stage) else "changed"


def spec_baseline_changed(root: Path, config: dict[str, str], ctx: dict[str, str]) -> bool:
    """人間が承認した仕様が、承認後に変更されているか。

    仕様 stage だけは `artifacts_hash` ではなく既存の spec 承認で判定する。
    baseline を成立させるのは Gate の PASS ではなく人間の承認だからである。
    まだ一度も承認されていない feature は対象外（通常フローの範囲）。
    """
    approval, _ = find_spec_approval(root, config, ctx["feature_dir"])

    if approval is None:
        return False

    ok, _ = check_spec_baseline(root, config, ctx)

    return not ok


def stale_stages(root: Path, config: dict[str, str], ctx: dict[str, str],
                 before: str = "") -> list[str]:
    """通過後に成果物が変更された stage を、stages 順で返す。

    先頭が最も上流の変更点であり、そこから下流はすべて再確認が必要になる。

    ``before`` を指定すると、その stage より前（= 上流）だけを見る。
    「stage X を実行してよいか」は、X が依存する上流だけで決まるためである。
    """
    stages = split_list(config.get("stages", ""))

    if before and before in stages:
        stages = stages[: stages.index(before)]

    stale = []

    for stage in stages:
        if stage == spec_stage(config):
            if spec_baseline_changed(root, config, ctx):
                stale.append(stage)
        elif stage_baseline_state(root, config, ctx, stage) == "changed":
            stale.append(stage)

    return stale


def describe_stale(config: dict[str, str], stale: list[str]) -> list[str]:
    """stale 検出時に人間へ出す案内。runner は自動で再開しない。"""
    stages = split_list(config.get("stages", ""))
    head = stale[0]
    downstream = stages[stages.index(head) + 1:] if head in stages else []

    lines = [
        "通過済み stage の成果物が、その stage の判定後に変更されています。",
        f"  変更が検出された stage: {', '.join(stale)}",
    ]

    if downstream:
        lines.append(f"  再確認が必要な下流 stage: {', '.join(downstream)}")

    lines += [
        "",
        "古い判定を完成扱いにしないため、ここで停止します。",
        "どちらで再開するかは人間が決めてください。",
    ]

    if head == spec_stage(config):
        # 仕様 stage は再レビューのあと、人間の再承認が必要になる
        lines += [
            "  仕様を人間が直した場合     : --spec-review（そのあと人間が承認し直す）",
            f"  AIに作り直させる場合       : --rework {head}",
        ]
    else:
        lines += [
            f"  成果物を人間が直した場合   : --review-current {head}",
            f"  AIに作り直させる場合       : --rework {head}",
        ]

    return lines


# ---------------------------------------------------------------- 状態解決


class Action:
    """次にすべきこと。

    kind:
      run          Worker → Reviewer を1往復する
      fix          Worker(mode=fix) → Reviewer を1往復する
      retry        BLOCKED からの明示的な再試行。Worker → Reviewer を1往復する
      rework       通過済み stage の明示的なやり直し。Worker → Reviewer を1往復する
      review_note  Worker を動かさず、人間コメントつきで Reviewer だけ起動する
      review_only  Worker を動かさず、現在の成果物を Reviewer だけで見直す
      await_human  人間の承認待ちで停止する
      done         完了
      stop         BLOCKED が記録済み。報告して停止する（--retry-blocked で再試行）
      error        runner が継続を禁止した。BLOCKED記録を新規作成して停止する

    `retry` は resolve_action からは返らない。人間が --retry-blocked を
    明示したときだけ resolve_retry_action が組み立てる。
    """

    def __init__(self, kind: str, stage: str = "", record: Path | None = None, note: str = ""):
        self.kind = kind
        self.stage = stage
        self.record = record
        self.note = note

    def __repr__(self) -> str:
        return f"Action({self.kind}, stage={self.stage!r})"


def is_note_processed(root: Path, feature_dir: str, record: Path) -> bool:
    """その記録の人間コメントが、既に別の記録として処理済みかどうか。

    確定済み記録を書き換えずに処理済みを判定するため、後続記録の
    `triggered_by_record` が自分を指しているかで判断する。
    """
    for path in list_records(root, feature_dir):
        if path == record:
            continue

        referenced = read_front_matter(path).get("triggered_by_record", "")

        if referenced and Path(referenced).name == record.name:
            return True

    return False


def pending_human_note(root: Path, config: dict[str, str], feature_dir: str,
                       record: Path) -> str:
    """未処理の人間コメントを返す。なければ空文字。"""
    note = read_human_note(record, config.get("human_note_heading", ""))

    if not note:
        return ""

    return "" if is_note_processed(root, feature_dir, record) else note


def resolve_action(root: Path, config: dict[str, str], feature_dir: str) -> Action:
    """全stage横断で最新の Gate記録から、次にすべきことを決める。"""
    stages = split_list(config.get("stages", ""))

    if not stages:
        raise SystemExit("設定に stages がありません。")

    record = latest_record(root, feature_dir)

    if record is None:
        return Action("run", stages[0])

    front = read_front_matter(record)
    verdict = front.get("verdict", "")
    gate = front.get("gate", "")

    if verdict == "IN_PROGRESS":
        return Action("fix", gate, record)

    if verdict == "RETURN":
        target = front.get("return_to", "")
        if target not in stages:
            return Action("error", gate, record, f"return_to が不正です: {target!r}")
        return Action("run", target, record)

    if verdict == "BLOCKED":
        return Action("stop", gate, record, front.get("blocked_reason", ""))

    if verdict == "PASS":
        if gate not in stages:
            return Action("error", gate, record, f"gate が不正です: {gate!r}")

        human_gates = split_list(config.get("human_gates", ""))

        if gate in human_gates:
            # 未処理の人間コメントは、承認待ちより先に処理する
            note = pending_human_note(root, config, feature_dir, record)

            if note:
                return Action("review_note", gate, record, note)

            heading = config.get(f"approval_heading_{gate.lower()}", "")

            if not heading:
                return Action(
                    "error", gate, record,
                    f"{gate} は human_gates に含まれますが approval_heading_{gate.lower()} がありません",
                )

            if not is_approved(record, heading):
                return Action("await_human", gate, record)

        index = stages.index(gate)

        if index == len(stages) - 1:
            return Action("done", gate, record)

        return Action("run", stages[index + 1], record)

    return Action("error", gate, record, f"verdict が不正です: {verdict!r}")


def count_returns_to(root: Path, feature_dir: str, stage: str) -> int:
    count = 0

    for path in list_records(root, feature_dir):
        front = read_front_matter(path)
        if front.get("verdict") == "RETURN" and front.get("return_to") == stage:
            count += 1

    return count


# ---------------------------------------------------------------- モデル解決


def resolve_model(config: dict[str, str], role: str, overrides: dict[str, str]) -> tuple[str, str]:
    """role -> model class -> 実モデル。(クラス, 実モデル) を返す。

    実モデルが未設定（プレースホルダ）の場合は空文字を返す。
    """
    model_class = overrides.get(role) or config.get(f"role_{role}", "")

    if not model_class:
        raise SystemExit(f"role_{role} が設定にありません。")

    actual = config.get(f"model_{model_class}", "")

    return model_class, "" if is_placeholder(actual) else actual


# ---------------------------------------------------------------- 起動


def build_worker_instruction(stage: str, mode: str, ctx: dict[str, str],
                             allowed: list[str], record: Path | None,
                             root: Path, config: dict[str, str],
                             model_class: str) -> str:
    prompts = config.get(f"stage_{stage.lower()}_prompts", "")

    lines = [
        f"{WORKER_PROMPT} を参照してください。",
        "",
        f"stage: {stage}",
        f"mode: {mode}",
        f"対象機能フォルダ: {ctx['feature_dir']}/",
        f"コマンド/アプリ名: {ctx['app']}",
        f"対象機能名: {ctx['feature']}",
        f"実装ファイル: src/{ctx['app']}/features/{ctx['feature']}.py",
        f"テストファイル: tests/{ctx['app']}/features/test_{ctx['feature']}.py",
        f"委譲する個別プロンプト: {prompts}",
        f"変更してよいファイル: {', '.join(allowed)}",
        f"使用モデル区分: {model_class}",
    ]

    if record is not None:
        lines.append(f"Gate記録ファイル: {rel(root, record)}")

    lines.append("補足条件: なし")

    return "\n".join(lines)


def build_reviewer_instruction(stage: str, ctx: dict[str, str], record: Path,
                               root: Path, seq: int, causality: dict[str, str],
                               violations: list[str], human_note: str,
                               config: dict[str, str], model_class: str,
                               human_gate: bool, mode: str,
                               spec_hash: str = "",
                               artifacts_hash: str = "") -> str:
    lines = [
        f"{REVIEWER_PROMPT} を参照してください。",
        "",
        f"stage: {stage}",
        f"mode: {mode}",
        f"spec_hash: {spec_hash}",
        f"artifacts_hash: {artifacts_hash}",
        f"対象機能フォルダ: {ctx['feature_dir']}/",
        f"コマンド/アプリ名: {ctx['app']}",
        f"対象機能名: {ctx['feature']}",
        f"Gate記録ファイル: {rel(root, record)}",
        f"run_seq: {seq}",
        f"triggered_by: {causality['triggered_by']}",
        f"triggered_by_record: {causality['triggered_by_record']}",
        f"supersedes: {causality['supersedes']}",
        f"human_gate: {'yes' if human_gate else 'no'}",
        f"review_independence: {config.get('review_independence', 'separate_context')}",
        f"使用モデル区分: {model_class}",
        f"guard_violations: {', '.join(violations) if violations else 'なし'}",
        f"human_note: {human_note}",
        "補足条件: なし",
    ]

    return "\n".join(lines)


def build_argv(config: dict[str, str], instruction: str, model: str) -> list[str]:
    """カンマ区切りの argv テンプレートを展開する。shell を経由しない。"""
    template = config.get("ai_command", "")

    if is_placeholder(template):
        raise SystemExit(
            f"ai_command が設定されていません。{CONFIG_DOC} または {LOCAL_OVERRIDE} に記入してください。"
        )

    argv = []
    for item in template.split(","):
        item = item.strip()
        if not item:
            continue
        argv.append(item.replace("{instruction}", instruction).replace("{model}", model))

    return argv


def run_ai(root: Path, argv: list[str]) -> int:
    result = subprocess.run(argv, cwd=root)
    return result.returncode


# ---------------------------------------------------------------- 表示


def show(text: str = "") -> None:
    print(text)


def summarize(root: Path, record: Path) -> str:
    front = read_front_matter(record)

    seq = front.get("run_seq", "?")
    gate = front.get("gate", "?")
    verdict = front.get("verdict", "?")
    next_step = front.get("next_step", "")

    head = f"[{seq}] {gate:<4} {verdict}"
    if next_step:
        head += f" / {next_step}"

    detail = (
        f"       FINDING {front.get('findings_total', '?')}件"
        f"（未解決 {front.get('findings_open', '?')}）"
        f"  収束 {front.get('review_rounds', '?')}ラウンド"
    )

    viewpoint_total = front.get("viewpoint_total", "")
    if viewpoint_total:
        detail += f"  観点 {front.get('viewpoint_covered', '?')}/{viewpoint_total}"

    return f"{head}\n{detail}\n       記録: {rel(root, record)}"


def cmd_status(root: Path, config: dict[str, str], ctx: dict[str, str]) -> int:
    feature_dir = ctx["feature_dir"]
    action = resolve_action(root, config, feature_dir)
    record = latest_record(root, feature_dir)
    spec_preflight_ok: bool | None = None

    show(f"feature: {ctx['app']}/{ctx['feature']}")
    show(f"記録数: {len(list_records(root, feature_dir))}")

    if record is None:
        show("最新記録: なし（未着手）")
    else:
        show("最新記録:")
        show(summarize(root, record))

    show()
    show("仕様 baseline:")

    target = spec_path(root, config, ctx)

    if target is None or not target.exists():
        show(f"  仕様書なし（{rel(root, target) if target else 'spec_artifact 未設定'}）")
    else:
        current = file_hash(target)
        approved_record, _ = find_spec_approval(
            root, config, feature_dir, required_spec_hash=current,
        )
        if approved_record is None:
            approved_record, _ = find_spec_approval(root, config, feature_dir)
        ok, detail = check_spec_baseline(root, config, ctx)
        spec_preflight_ok = ok

        show(f"  仕様書: {rel(root, target)}（{current[:12]}...）")
        show(f"  人間の仕様承認: {rel(root, approved_record) if approved_record else 'なし'}")
        show(f"  製造開始条件: {'満たしている' if ok else '満たしていない'}")

        if not ok:
            for line in detail.splitlines():
                show(f"    {line}")

    show()
    show("stage 成果物の baseline:")

    labels = {
        "match": "通過時と同じ",
        "changed": "**通過後に変更あり**",
        "no_pass": "まだ PASS 記録がない",
        "unknown": "判定不能（記録に artifacts_hash がない、または未設定）",
    }

    for stage in split_list(config.get("stages", "")):
        if stage == spec_stage(config):
            # 仕様 stage は人間の承認が baseline を決めるため、上の仕様 baseline で判定する
            show(f"  {stage:<4} 上記の仕様 baseline で判定")
            continue

        state = stage_baseline_state(root, config, ctx, stage)
        show(f"  {stage:<4} {labels[state]}")

    stale = stale_stages(root, config, ctx)

    show()
    if (
        action.kind == "run"
        and action.stage
        and is_manufacturing_stage(config, action.stage)
        and spec_preflight_ok is False
    ):
        # 製造の手前で止まる場合は、既存の Manufacturing Preflight の説明を優先する
        show(f"次の動作: Manufacturing Preflight で停止 (stage={action.stage})")
    elif stale:
        show(f"次の動作: 通過済み成果物の変更を検出したため停止 ({', '.join(stale)})")
        for line in describe_stale(config, stale)[1:]:
            show(line)
    else:
        show(f"次の動作: {action.kind}" + (f" (stage={action.stage})" if action.stage else ""))

    if action.note:
        show(f"理由: {action.note}")

    if action.kind == "stop":
        show()
        show("BLOCKED は自動では再開しません。"
             "原因を解消したうえで --retry-blocked を明示してください。")

    if action.kind == "await_human" and action.stage == spec_stage(config):
        show()
        show("仕様承認待ちです。Gate記録の承認欄にチェックを入れると製造へ進みます。")
        show("仕様を修正した場合は、--spec-review で再レビューしてから承認してください。")

    return 0


def cmd_history(root: Path, ctx: dict[str, str]) -> int:
    records = list_records(root, ctx["feature_dir"])

    if not records:
        show("Gate記録がありません。")
        return 0

    show(f"feature: {ctx['app']}/{ctx['feature']}")
    show()

    for path in records:
        front = read_front_matter(path)
        seq = front.get("run_seq", path.name.split("_", 1)[0])
        gate = front.get("gate", "?")
        verdict = front.get("verdict", "?")

        line = f"{seq:>4}  {gate:<4}  {verdict}"

        if verdict == "RETURN":
            line += f" → {front.get('return_to', '?')}"
        elif verdict == "BLOCKED":
            line += f" ({front.get('blocked_reason', '')})"

        show(line)

        spec = front.get("spec_hash", "")
        if spec:
            show(f"          spec {spec[:12]}...")

        triggered = front.get("triggered_by_record", "")
        if triggered:
            show(f"          ← {triggered} による再実行")

        supersedes = front.get("supersedes", "")
        if supersedes:
            show(f"          ← {supersedes} を置き換え")

        show(f"          {path.name}")

    return 0


# ---------------------------------------------------------------- 実行


def last_record_of_stage(root: Path, feature_dir: str, stage: str) -> str:
    """その stage の直近の確定記録のパス（supersedes 用）。"""
    for path in reversed(list_records(root, feature_dir)):
        front = read_front_matter(path)
        if front.get("gate") == stage and front.get("verdict") in TERMINAL_VERDICTS:
            return rel(root, path)

    return ""


def compute_causality(root: Path, feature_dir: str, stage: str,
                      previous: Path | None, kind: str) -> dict[str, str]:
    """新しい Gate記録の因果情報を決める。

    runner の分岐には使わない。人間が「どの指摘でどこへ戻ったか」を
    追跡するための情報。
    """
    empty = {"triggered_by": "INITIAL", "triggered_by_record": "", "supersedes": ""}

    if previous is None:
        return empty

    if kind == "review_note":
        return {
            "triggered_by": "HUMAN_NOTE",
            "triggered_by_record": rel(root, previous),
            "supersedes": "",
        }

    if kind == "review_only":
        return {
            "triggered_by": "MANUAL",
            "triggered_by_record": "",
            "supersedes": last_record_of_stage(root, feature_dir, stage),
        }

    if kind == "retry":
        return {
            "triggered_by": "RETRY_BLOCKED",
            "triggered_by_record": rel(root, previous),
            "supersedes": "",
        }

    if kind == "rework":
        return {
            "triggered_by": "REWORK",
            "triggered_by_record": "",
            "supersedes": last_record_of_stage(root, feature_dir, stage),
        }

    if read_front_matter(previous).get("verdict") == "RETURN":
        return {
            "triggered_by": "RETURN",
            "triggered_by_record": rel(root, previous),
            "supersedes": last_record_of_stage(root, feature_dir, stage),
        }

    return empty


def write_runner_record(root: Path, ctx: dict[str, str], stage: str, reason: str,
                        detail: str, previous: Path | None,
                        violations: list[str] | None = None) -> Path:
    """runner 自身が処理継続を禁止した場合の BLOCKED記録を新規作成する。

    画面ではなくファイルが正式記録であるため、runner が止めた場合も記録を残す。
    既存の確定記録は書き換えない。
    """
    record = new_record_path(root, ctx["feature_dir"], stage)
    record.parent.mkdir(parents=True, exist_ok=True)

    seq = int(record.name.split("_", 1)[0])
    stamp = now().isoformat(timespec="seconds")

    front = {
        "schema": "gate_record/v1",
        "feature": f"{ctx['app']}/{ctx['feature']}",
        "gate": stage,
        "run_seq": seq,
        "mode": "auto",
        "recorded_by": "runner",
        "verdict": "BLOCKED",
        "next_step": "STOP",
        "return_to": "",
        "blocked_reason": reason,
        "triggered_by": "RUNNER",
        "triggered_by_record": rel(root, previous) if previous else "",
        "supersedes": "",
        "started_at": stamp,
        "finished_at": stamp,
        "review_rounds": 0,
        "findings_total": 0,
        "findings_open": 0,
        "guard_violations": len(violations or []),
        "req_total": "",
        "req_covered": "",
        "viewpoint_total": "",
        "viewpoint_covered": "",
        "review_independence": "",
        "model_design": "",
        "model_build": "",
        "model_review": "",
        "artifacts": "",
        "human_decision_required": 1,
    }

    lines = ["---"]
    lines.extend(f"{key}: {value}" for key, value in front.items())
    lines += [
        "---",
        "",
        f"# Gate記録（runner による停止） — {stage}",
        "",
        "## 判定サマリ",
        "",
        "| 項目 | 値 |",
        "|---|---|",
        f"| stage | {stage} |",
        "| verdict | BLOCKED |",
        "| next_step | STOP |",
        f"| blocked_reason | {reason} |",
        "| 記録者 | runner |",
        "",
        "**この記録は runner が作成しました。** AIレビューの結果ではなく、"
        "runner が処理の継続を禁止したことを示します。",
        "",
        "## 停止の理由",
        "",
        detail,
        "",
        "## 変更範囲のガード",
        "",
    ]

    if violations:
        lines.extend(f"- {path}" for path in violations)
    else:
        lines.append("- 該当なし")

    lines += [
        "",
        "## 人間確認欄",
        "",
        "今回は対象外（runner による停止のため、AIレビューを実施していません）。",
        "",
        "## 作業後報告",
        "",
        "- runner が停止したため、この stage のAIレビューは実施していません。",
        "- 原因を解消したうえで、runner を再実行してください。",
        "- **この記録は変更しません。再実行時は新しい記録が作成されます。**",
    ]

    record.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record


def stage_setup(config: dict[str, str], ctx: dict[str, str], stage: str,
                overrides: dict[str, str]) -> dict:
    key = stage.lower()

    worker_allowed = expand(config.get(f"stage_{key}_worker", ""), ctx)
    reviewer_allowed = expand(config.get(f"stage_{key}_reviewer", ""), ctx)

    if not worker_allowed or not reviewer_allowed:
        raise SystemExit(f"stage_{key}_worker / stage_{key}_reviewer が設定にありません。")

    worker_role = config.get(f"stage_{key}_worker_role", "design")
    reviewer_role = config.get("reviewer_role", "review")

    worker_class, worker_model = resolve_model(config, worker_role, overrides)
    reviewer_class, reviewer_model = resolve_model(config, reviewer_role, overrides)

    return {
        "worker_allowed": worker_allowed,
        "reviewer_allowed": reviewer_allowed,
        "worker_role": worker_role,
        "reviewer_role": reviewer_role,
        "worker_class": worker_class,
        "worker_model": worker_model,
        "reviewer_class": reviewer_class,
        "reviewer_model": reviewer_model,
        "human_gate": stage in split_list(config.get("human_gates", "")),
    }


def run_worker(root: Path, config: dict[str, str], ctx: dict[str, str], stage: str,
               mode: str, record: Path | None, setup: dict) -> tuple[bool, list[str]]:
    """Worker を別プロセスで起動し、実行前後の差分でガードする。"""
    instruction = build_worker_instruction(
        stage, mode, ctx, setup["worker_allowed"], record, root, config,
        setup["worker_class"],
    )
    argv = build_argv(config, instruction, setup["worker_model"])

    show(f"Worker   {stage} mode={mode} class={setup['worker_class']}")

    before = snapshot(root)
    code = run_ai(root, argv)
    after = snapshot(root)

    if code != 0:
        show(f"  Worker が異常終了しました（exit={code}）")
        return False, []

    violations = check_guard(diff_snapshots(before, after), setup["worker_allowed"])

    if violations:
        show(f"  範囲外の変更を検出: {len(violations)}件")
        for path in violations:
            show(f"    - {path}")

    return True, violations


def current_spec_hash(root: Path, config: dict[str, str], ctx: dict[str, str],
                      stage: str) -> str:
    """仕様 stage のときだけ、現在の仕様書のハッシュを返す。

    ハッシュは runner が計算する。Reviewer は転記するだけで、
    製造開始時に runner が再計算して照合する（AIの計算に依存しない）。
    """
    if stage != spec_stage(config):
        return ""

    target = spec_path(root, config, ctx)

    return file_hash(target) if target and target.exists() else ""


def run_reviewer(root: Path, config: dict[str, str], ctx: dict[str, str], stage: str,
                 record: Path, seq: int, causality: dict[str, str], setup: dict,
                 violations: list[str], human_note: str,
                 review_mode: str) -> tuple[bool, list[str]]:
    """Reviewer を別プロセスで起動する。成果物は変更しない。"""
    record.parent.mkdir(parents=True, exist_ok=True)

    instruction = build_reviewer_instruction(
        stage, ctx, record, root, seq, causality, violations, human_note,
        config, setup["reviewer_class"], setup["human_gate"], review_mode,
        current_spec_hash(root, config, ctx, stage),
        current_artifacts_hash(root, config, ctx, stage),
    )
    argv = build_argv(config, instruction, setup["reviewer_model"])

    show(f"Reviewer {stage} class={setup['reviewer_class']}")

    before = snapshot(root)
    code = run_ai(root, argv)
    after = snapshot(root)

    if code != 0:
        show(f"  Reviewer が異常終了しました（exit={code}）")
        return False, []

    own = check_guard(diff_snapshots(before, after), setup["reviewer_allowed"])

    if own:
        show(f"  Reviewer が範囲外を変更しました: {len(own)}件")
        for path in own:
            show(f"    - {path}")

    return True, own


def show_dry_run(root: Path, config: dict[str, str], ctx: dict[str, str], stage: str,
                 kind: str, mode: str, setup: dict, record: Path,
                 causality: dict[str, str], human_note: str) -> None:
    show(f"--- dry-run: stage={stage} kind={kind} mode={mode}")

    if kind in ("run", "fix", "retry", "rework"):
        instruction = build_worker_instruction(
            stage, mode, ctx, setup["worker_allowed"],
            record if mode == "fix" else None, root, config, setup["worker_class"],
        )
        try:
            argv = build_argv(config, instruction, setup["worker_model"])
        except SystemExit as error:
            argv = [f"(組み立て不可: {error})"]

        show(f"Worker   role={setup['worker_role']} class={setup['worker_class']} "
             f"model={setup['worker_model'] or '(未設定)'}")
        show(f"  変更してよい: {', '.join(setup['worker_allowed'])}")
        show(f"  argv: {argv}")
    else:
        show("Worker   起動しない（現在の成果物をそのまま Reviewer へ渡す）")

    show(f"Reviewer role={setup['reviewer_role']} class={setup['reviewer_class']} "
         f"model={setup['reviewer_model'] or '(未設定)'}")
    show(f"  変更してよい: {', '.join(setup['reviewer_allowed'])}")
    show(f"  human_gate: {'yes' if setup['human_gate'] else 'no'}")
    show(f"  Gate記録: {rel(root, record)}")
    show(f"  triggered_by={causality['triggered_by']} "
         f"triggered_by_record={causality['triggered_by_record']} "
         f"supersedes={causality['supersedes']}")
    show(f"  human_note: {human_note or '(なし)'}")

    spec = current_spec_hash(root, config, ctx, stage)
    if spec:
        show(f"  spec_hash: {spec[:12]}...")

    artifacts = current_artifacts_hash(root, config, ctx, stage)
    if artifacts:
        show(f"  artifacts_hash: {artifacts[:12]}...")


def execute(root: Path, config: dict[str, str], ctx: dict[str, str],
            action: Action, overrides: dict[str, str], dry_run: bool) -> Path | None:
    """1回分の実行。Gate記録のパスを返す。失敗時は None。"""
    stage = action.stage
    setup = stage_setup(config, ctx, stage, overrides)

    with_worker = action.kind in ("run", "fix", "retry", "rework")
    mode = "fix" if action.kind == "fix" else "create"

    if action.kind == "fix":
        record = action.record
        seq = int(read_front_matter(record).get("run_seq", "0") or 0)
        causality = {"triggered_by": "", "triggered_by_record": "", "supersedes": ""}
        human_note = ""
    else:
        record = new_record_path(root, ctx["feature_dir"], stage)
        seq = int(record.name.split("_", 1)[0])
        causality = compute_causality(
            root, ctx["feature_dir"], stage, action.record, action.kind
        )
        # note を人間コメントとして扱うのは review_note だけ。
        # retry では note が blocked_reason（表示用）なので Reviewer へ渡さない。
        human_note = action.note if action.kind == "review_note" else ""

    if dry_run:
        show_dry_run(root, config, ctx, stage, action.kind, mode, setup,
                     record, causality, human_note)
        return None

    violations: list[str] = []

    if with_worker:
        ok, violations = run_worker(
            root, config, ctx, stage, mode,
            record if mode == "fix" else None, setup,
        )

        if not ok:
            write_runner_record(
                root, ctx, stage, "state_error",
                "Worker が異常終了しました。AI CLI の設定と実行環境を確認してください。",
                action.record,
            )
            return None

    review_mode = "manual" if action.kind == "review_only" else "auto"

    ok, own = run_reviewer(
        root, config, ctx, stage, record, seq, causality, setup,
        violations, human_note, review_mode,
    )

    if not ok:
        write_runner_record(
            root, ctx, stage, "state_error",
            "Reviewer が異常終了しました。AI CLI の設定と実行環境を確認してください。",
            action.record,
        )
        return None

    if own:
        write_runner_record(
            root, ctx, stage, "guard_violation",
            "Reviewer が、許可されていないファイルを変更しました。Reviewer は Gate記録"
            "（CP3 では 25_review_result.md も）以外を変更できません。",
            record, own,
        )
        return None

    if not record.exists():
        write_runner_record(
            root, ctx, stage, "state_error",
            f"Reviewer が Gate記録を作成しませんでした: {rel(root, record)}",
            action.record,
        )
        return None

    show(summarize(root, record))
    return record


# ---------------------------------------------------------------- メインループ


def halt(root: Path, ctx: dict[str, str], stage: str, reason: str, detail: str,
         previous: Path | None, violations: list[str] | None = None,
         dry_run: bool = False) -> int:
    """runner が継続を禁止する。正式な BLOCKED記録を残してから停止する。

    `--dry-run` は「実行せず表示する」ための入口なので、記録を作らない。
    作ってしまうと、確認しただけで Gate履歴が増えてしまう。
    """
    show(detail)

    if dry_run:
        show(f"（dry-run のため BLOCKED記録は作成しません: {reason}）")
        return 1

    record = write_runner_record(root, ctx, stage, reason, detail, previous, violations)
    show(f"BLOCKED記録を作成しました: {rel(root, record)}")
    return 1


def resolve_retry_action(root: Path, config: dict[str, str], feature_dir: str) -> Action:
    """BLOCKED からの明示的な再試行を組み立てる。

    最新の Gate記録が BLOCKED のときだけ受け付ける。
    過去の BLOCKED記録は削除も上書きもしない。
    """
    record = latest_record(root, feature_dir)

    if record is None:
        raise SystemExit(
            "Gate記録がありません。--retry-blocked は BLOCKED記録がある場合だけ使えます。"
        )

    front = read_front_matter(record)
    verdict = front.get("verdict", "")

    if verdict != "BLOCKED":
        raise SystemExit(
            f"最新の Gate記録は BLOCKED ではありません（verdict: {verdict or '不明'}）。\n"
            "--retry-blocked は BLOCKED からの復旧専用です。"
            "通常の実行は --retry-blocked なしで行ってください。"
        )

    stage = front.get("gate", "")

    if stage not in split_list(config.get("stages", "")):
        raise SystemExit(f"BLOCKED記録の gate が不正です: {stage!r}")

    return Action("retry", stage, record, front.get("blocked_reason", ""))


def cmd_run(root: Path, config: dict[str, str], ctx: dict[str, str],
            overrides: dict[str, str], once: bool, dry_run: bool,
            review_current: str = "", retry_blocked: bool = False,
            spec_review: bool = False, rework: str = "") -> int:
    feature_dir = ctx["feature_dir"]
    stages = split_list(config.get("stages", ""))
    max_rounds = int(config.get("max_rounds", "3"))
    max_returns = int(config.get("max_returns_per_gate", "3"))
    fix_rounds = 0

    exclusive = [
        name for name, value in (
            ("--review-current", bool(review_current)),
            ("--retry-blocked", retry_blocked),
            ("--spec-review", spec_review),
            ("--rework", bool(rework)),
        ) if value
    ]

    if len(exclusive) > 1:
        raise SystemExit(f"{' と '.join(exclusive)} は同時に指定できません。")

    # --- 仕様レビューの単独実行：製造 runner とは独立して何度でも回せる
    if spec_review:
        stage = spec_stage(config)

        if stage not in stages:
            raise SystemExit(f"設定の spec_stage が不正です: {stage!r}")

        target = spec_path(root, config, ctx)

        if target is None or not target.exists():
            raise SystemExit(
                f"仕様書がありません: {rel(root, target) if target else '(spec_artifact 未設定)'}\n"
                "仕様レビューは、既存の仕様書に対して行います。"
            )

        show(f"仕様レビュー（単独実行）: {rel(root, target)}")
        show(f"  spec_hash: {file_hash(target)[:12]}...")
        review_current = stage

    # --- マニュアル介入からの復帰：Worker を動かさず Reviewer だけを起動する
    if review_current:
        if review_current not in stages:
            raise SystemExit(
                f"--review-current の値が stages にありません: {review_current!r}"
            )

        action = Action("review_only", review_current, latest_record(root, feature_dir))
        record = execute(root, config, ctx, action, overrides, dry_run)

        if dry_run:
            return 0

        return 0 if record is not None else 1

    # --- 通過済み stage からのやり直し：人間が stage を明示したときだけ行う
    if rework:
        if rework not in stages:
            raise SystemExit(f"--rework の値が stages にありません: {rework!r}")

    pending_retry = retry_blocked
    pending_rework = rework

    while True:
        if pending_retry:
            action = resolve_retry_action(root, config, feature_dir)
            pending_retry = False

            show(f"BLOCKED からの再試行: {action.stage}"
                 f"（blocked_reason: {action.note or '不明'}）")
            show(f"  元の記録: {rel(root, action.record)}（変更せず履歴として残します）")
        elif pending_rework:
            action = Action("rework", pending_rework, latest_record(root, feature_dir))
            pending_rework = ""

            show(f"通過済み stage のやり直し: {action.stage}")
            show("  過去の Gate記録は変更せず、新しい記録を追加します。")
        else:
            action = resolve_action(root, config, feature_dir)

        # 完了・承認待ちと判定する前に、通過済み成果物が変わっていないかを確認する。
        # ここは Worker を起動しないため Manufacturing Preflight が働かない。
        # 古い PASS をそのまま完成扱いにしないための、最後の関門になる。
        if action.kind in ("done", "await_human"):
            stale = stale_stages(root, config, ctx)

            if stale:
                for line in describe_stale(config, stale):
                    show(line)
                return 1

        if action.kind == "done":
            show("完了しました。")
            show(summarize(root, action.record))
            return 0

        if action.kind == "await_human":
            show(f"{action.stage} で停止しました。人間の判断が必要です。")
            show(summarize(root, action.record))
            show()
            show("Gate記録の人間確認欄へ回答し、承認欄にチェックを入れてから再実行してください。")
            show("気になる点を自然文で記入した場合は、再実行時に Reviewer が戻り先を判定します。")
            return 0

        if action.kind == "stop":
            show(f"{action.stage} で停止しています: {action.note}")
            if action.record is not None:
                show(summarize(root, action.record))
            show()
            show("BLOCKED は自動では再開しません。")
            show("原因を解消したうえで、--retry-blocked を明示して再試行してください。")
            show(f"  python tools/feature_runner.py --feature "
                 f"{ctx['app']}/{ctx['feature']} --retry-blocked")
            return 1

        if action.kind == "error":
            return halt(
                root, ctx, action.stage or (stages[0] if stages else "?"),
                "state_error",
                f"状態遷移を解決できません: {action.note}",
                action.record, dry_run=dry_run,
            )

        if action.kind == "fix":
            fix_rounds += 1
            if fix_rounds >= max_rounds:
                return halt(
                    root, ctx, action.stage, "non_convergence",
                    f"収束ループが上限に達しました（max_rounds={max_rounds}）。",
                    action.record, dry_run=dry_run,
                )
        elif action.kind in ("run", "retry", "rework"):
            fix_rounds = 0
            if (action.kind == "run"
                    and count_returns_to(root, feature_dir, action.stage) >= max_returns):
                return halt(
                    root, ctx, action.stage, "non_convergence",
                    f"{action.stage} への差し戻しが上限に達しました"
                    f"（max_returns_per_gate={max_returns}）。",
                    action.record, dry_run=dry_run,
                )

        # --- Manufacturing Preflight
        # 製造 stage で Worker を動かす前に、承認済み仕様 baseline を確認する。
        # Reviewer だけの動作（review_only / review_note）は読み取りのため対象外。
        if (action.kind in ("run", "fix", "retry", "rework")
                and is_manufacturing_stage(config, action.stage)):
            ok, detail = check_spec_baseline(root, config, ctx)

            if not ok:
                show(f"製造を開始できません（{action.stage} の手前で停止）。")
                return halt(
                    root, ctx, spec_stage(config), "spec_not_approved",
                    f"Manufacturing Preflight に失敗しました。\n{detail}",
                    action.record, dry_run=dry_run,
                )

        # --- 上流成果物の変更チェック
        # stage を通常進行で実行する前に、その stage が依存する上流が
        # 通過時のままかを確認する。古い G2 のまま CP3 を作らせないため。
        # 自分自身は作り直す対象なので見ない。
        # 明示的な人間の操作（rework / retry / review_only / review_note）は、
        # 変更を承知のうえの指示なので止めない。
        # 仕様 stage は上の Manufacturing Preflight が担当する。
        if action.kind == "run":
            stale = stale_stages(root, config, ctx, before=action.stage)

            if stale:
                show(f"{action.stage} を実行できません。")
                for line in describe_stale(config, stale):
                    show(line)
                return 1

        record = execute(root, config, ctx, action, overrides, dry_run)

        if dry_run:
            return 0

        if record is None:
            return 1

        if once:
            return 0


# ---------------------------------------------------------------- エントリポイント


def build_context(root: Path, feature: str) -> dict[str, str]:
    if "/" not in feature:
        raise SystemExit(
            "--feature は <command_or_app_name>/<feature_name> の形式で指定してください。"
        )

    app, name = feature.split("/", 1)
    feature_dir = f"docs/{app}/features/{name}"

    if not (root / feature_dir).exists():
        raise SystemExit(f"対象機能フォルダが見つかりません: {feature_dir}")

    return {"app": app, "feature": name, "feature_dir": feature_dir}


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="feature オートモードの runner。Worker と Reviewer を別プロセスで交互に起動する。"
    )
    parser.add_argument("--feature", required=True, help="<command_or_app_name>/<feature_name>")
    parser.add_argument("--once", action="store_true", help="1 stage だけ進める")
    parser.add_argument("--dry-run", action="store_true", help="実行せず、次の動作と argv を表示する")
    parser.add_argument("--status", action="store_true", help="現在状態を表示する")
    parser.add_argument("--history", action="store_true", help="Gate記録の連鎖を表示する")
    parser.add_argument(
        "--review-current",
        metavar="STAGE",
        help="Worker を起動せず、現在の成果物をそのまま Reviewer に見直させる"
        "（マニュアル介入からの復帰）",
    )
    parser.add_argument(
        "--retry-blocked",
        action="store_true",
        help="最新 Gate が BLOCKED のとき、その stage を明示的に再試行する"
        "（BLOCKED からの復旧。過去の記録は残す）",
    )
    parser.add_argument(
        "--rework",
        metavar="STAGE",
        help="通過済みの stage を Worker から明示的にやり直す"
        "（完成後の修正。過去の記録は残す）",
    )
    parser.add_argument(
        "--spec-review",
        action="store_true",
        help="仕様書（20_spec.md）のAIレビューだけを単独実行する。"
        "製造は開始しない。何度でも実行できる",
    )
    parser.add_argument("--role-design", help="design のモデルクラスを上書きする")
    parser.add_argument("--role-build", help="build のモデルクラスを上書きする")
    parser.add_argument("--role-review", help="review のモデルクラスを上書きする")

    args = parser.parse_args()

    root = repo_root()
    config = read_config(root)
    ctx = build_context(root, args.feature)

    overrides = {
        role: value
        for role, value in (
            ("design", args.role_design),
            ("build", args.role_build),
            ("review", args.role_review),
        )
        if value
    }

    if args.history:
        raise SystemExit(cmd_history(root, ctx))

    if args.status:
        raise SystemExit(cmd_status(root, config, ctx))

    raise SystemExit(
        cmd_run(
            root, config, ctx, overrides, args.once, args.dry_run,
            args.review_current or "", args.retry_blocked, args.spec_review,
            args.rework or "",
        )
    )


if __name__ == "__main__":
    main()

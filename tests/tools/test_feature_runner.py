"""tools/feature_runner.py の単体テスト。

AI CLI を起動しない範囲だけを検証する。
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import feature_runner as fr  # noqa: E402


# ---------------------------------------------------------------- フラットな key: value


def test_parse_flat_reads_key_value():
    text = "role_design = standard\nrole_build = cheap\n"
    assert fr.parse_flat(text, "=") == {
        "role_design": "standard",
        "role_build": "cheap",
    }


def test_parse_flat_skips_comments_and_blank_lines():
    text = "# コメント\n\nrole_review = standard\n"
    assert fr.parse_flat(text, "=") == {"role_review": "standard"}


def test_parse_flat_splits_only_on_first_separator():
    """front matter の値に区切り文字が含まれても壊れないこと。"""
    text = "started_at: 2026-08-22T18:30:00+09:00\n"
    assert fr.parse_flat(text, ":") == {"started_at": "2026-08-22T18:30:00+09:00"}


def test_parse_flat_keeps_empty_value():
    assert fr.parse_flat("return_to:\n", ":") == {"return_to": ""}


def test_split_list_drops_empty_items():
    assert fr.split_list("a, b ,, c") == ["a", "b", "c"]


# ---------------------------------------------------------------- 設定ブロックと front matter


def test_extract_fenced_block():
    text = "説明\n\n```feature_loop\nrole_design = standard\n```\n\n続き\n"
    assert fr.extract_fenced_block(text, "feature_loop").strip() == "role_design = standard"


def test_extract_fenced_block_returns_empty_when_missing():
    assert fr.extract_fenced_block("本文だけ", "feature_loop") == ""


def test_read_config_from_actual_rule_document():
    """実際の 70_feature_loop.md から設定を読めること。"""
    config = fr.read_config(REPO_ROOT)

    assert config["stages"] == "G0, CP1, G2, CP3"
    assert config["human_gates"] == "CP1, CP3"
    assert config["role_build"] == "cheap"
    assert "stage_cp3_reviewer" in config


def test_read_config_applies_local_override(tmp_path):
    doc = tmp_path / fr.CONFIG_DOC
    doc.parent.mkdir(parents=True)
    doc.write_text("```feature_loop\nmodel_cheap = A\n```\n", encoding="utf-8")

    local = tmp_path / fr.LOCAL_OVERRIDE
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text("model_cheap = B\n", encoding="utf-8")

    assert fr.read_config(tmp_path)["model_cheap"] == "B"


def write_record(directory: Path, name: str, **fields) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    lines.extend(f"{key}: {value}" for key, value in fields.items())
    lines.append("---")
    lines.append("")
    lines.append("# Gate記録")
    path = directory / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_read_front_matter(tmp_path):
    path = write_record(tmp_path, "0001_x_g0.md", verdict="PASS", gate="G0", return_to="")
    front = fr.read_front_matter(path)

    assert front["verdict"] == "PASS"
    assert front["gate"] == "G0"
    assert front["return_to"] == ""


def test_read_front_matter_returns_empty_without_block(tmp_path):
    path = tmp_path / "plain.md"
    path.write_text("# 見出しだけ\n", encoding="utf-8")
    assert fr.read_front_matter(path) == {}


# ---------------------------------------------------------------- Gate記録


@pytest.fixture
def feature(tmp_path):
    """docs/<app>/features/<feature>/ を持つ一時リポジトリ。"""
    feature_dir = "docs/demo_app/features/demo"
    (tmp_path / feature_dir / "gates").mkdir(parents=True)
    return tmp_path, feature_dir


def test_list_records_is_sorted_by_sequence(feature):
    root, feature_dir = feature
    gates = root / feature_dir / "gates"

    write_record(gates, "0010_20260101T000000_g2.md", verdict="PASS", gate="G2")
    write_record(gates, "0002_20260101T000000_cp1.md", verdict="PASS", gate="CP1")

    names = [p.name for p in fr.list_records(root, feature_dir)]
    assert names == ["0002_20260101T000000_cp1.md", "0010_20260101T000000_g2.md"]


def test_next_seq_increments(feature):
    root, feature_dir = feature
    assert fr.next_seq(root, feature_dir) == 1

    write_record(root / feature_dir / "gates", "0007_x_g0.md", verdict="PASS", gate="G0")
    assert fr.next_seq(root, feature_dir) == 8


def test_new_record_path_does_not_overwrite(feature):
    root, feature_dir = feature
    first = fr.new_record_path(root, feature_dir, "CP1")
    first.write_text("既存", encoding="utf-8")

    # 同じ連番・同じ秒でも、既存ファイルを潰さない名前になること
    monkey = fr.new_record_path(root, feature_dir, "CP1")
    assert monkey != first


# ---------------------------------------------------------------- 状態解決


CONFIG = {
    "stages": "G0, CP1, G2, CP3",
    "human_gates": "CP1, CP3",
    "approval_heading_cp1": "下流進行承認",
    "approval_heading_cp3": "受け入れ判断",
}


def test_resolve_action_starts_at_first_stage(feature):
    root, feature_dir = feature
    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert action.kind == "run"
    assert action.stage == "G0"


def test_resolve_action_advances_after_ai_gate_pass(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0001_x_g0.md", verdict="PASS", gate="G0")

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert (action.kind, action.stage) == ("run", "CP1")


def test_resolve_action_waits_for_human_at_human_gate(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0002_x_cp1.md", verdict="PASS", gate="CP1")

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert action.kind == "await_human"


def test_resolve_action_continues_after_human_approval(feature):
    root, feature_dir = feature
    path = write_record(root / feature_dir / "gates", "0002_x_cp1.md", verdict="PASS", gate="CP1")
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n### 下流進行承認\n\n- [x] 回答した\n- [x] 承認する\n",
        encoding="utf-8",
    )

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert (action.kind, action.stage) == ("run", "G2")


def test_resolve_action_resumes_in_progress_as_fix(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0002_x_cp1.md", verdict="IN_PROGRESS", gate="CP1")

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert (action.kind, action.stage) == ("fix", "CP1")


def test_resolve_action_follows_return_target(feature):
    root, feature_dir = feature
    gates = root / feature_dir / "gates"

    write_record(gates, "0003_x_g2.md", verdict="PASS", gate="G2")
    write_record(gates, "0004_x_cp3.md", verdict="RETURN", gate="CP3", return_to="G2")

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert (action.kind, action.stage) == ("run", "G2")


def test_resolve_action_uses_cross_stage_latest_not_per_stage(feature):
    """RETURN 直後に、差し戻し前の古い PASS を採用しないこと。

    stage 別の最新を読む実装だと、CP3 の RETURN を見落として
    「G2 は PASS 済みだから CP3 へ」と誤って進んでしまう。
    """
    root, feature_dir = feature
    gates = root / feature_dir / "gates"

    write_record(gates, "0003_x_g2.md", verdict="PASS", gate="G2")
    write_record(gates, "0004_x_cp3.md", verdict="RETURN", gate="CP3", return_to="G2")

    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert action.stage == "G2", "CP3 の RETURN より前の G2 PASS を採用してはいけない"
    assert action.record is not None
    assert action.record.name == "0004_x_cp3.md"


def test_resolve_action_stops_on_blocked(feature):
    root, feature_dir = feature
    write_record(
        root / feature_dir / "gates",
        "0001_x_g0.md",
        verdict="BLOCKED",
        gate="G0",
        blocked_reason="business_decision",
    )

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert action.kind == "stop"
    assert action.note == "business_decision"


def test_resolve_action_done_after_last_stage_approved(feature):
    root, feature_dir = feature
    path = write_record(root / feature_dir / "gates", "0006_x_cp3.md", verdict="PASS", gate="CP3")
    path.write_text(
        path.read_text(encoding="utf-8") + "\n### 受け入れ判断\n\n- [x] 受け入れる\n",
        encoding="utf-8",
    )

    assert fr.resolve_action(root, CONFIG, feature_dir).kind == "done"


def test_count_returns_to(feature):
    root, feature_dir = feature
    gates = root / feature_dir / "gates"

    write_record(gates, "0001_x_cp3.md", verdict="RETURN", gate="CP3", return_to="G2")
    write_record(gates, "0002_x_cp3.md", verdict="RETURN", gate="CP3", return_to="G2")
    write_record(gates, "0003_x_cp3.md", verdict="RETURN", gate="CP3", return_to="CP1")

    assert fr.count_returns_to(root, feature_dir, "G2") == 2
    assert fr.count_returns_to(root, feature_dir, "CP1") == 1


# ---------------------------------------------------------------- 人間確認欄


def test_is_approved_requires_all_boxes_checked(tmp_path):
    path = tmp_path / "record.md"
    path.write_text("### 下流進行承認\n\n- [x] A\n- [ ] B\n", encoding="utf-8")

    assert fr.is_approved(path, "下流進行承認") is False


def test_is_approved_ignores_unchecked_options_outside_section(tmp_path):
    """「判断してほしいこと」の排他選択肢は未チェックが残るが、承認判定に影響しないこと。"""
    path = tmp_path / "record.md"
    path.write_text(
        "### 判断してほしいこと\n\n- [x] AI案で確定\n- [ ] 別案で確定\n\n"
        "### 下流進行承認\n\n- [x] 回答した\n- [x] 承認する\n",
        encoding="utf-8",
    )

    assert fr.is_approved(path, "下流進行承認") is True


def test_is_approved_false_when_section_missing(tmp_path):
    path = tmp_path / "record.md"
    path.write_text("### 別の見出し\n\n- [x] A\n", encoding="utf-8")

    assert fr.is_approved(path, "下流進行承認") is False


def test_read_human_note(tmp_path):
    path = tmp_path / "record.md"
    path.write_text(
        "### 気になる点\n\n```text\n空入力のときの試験が無い気がする\n```\n",
        encoding="utf-8",
    )

    assert fr.read_human_note(path, "気になる点") == "空入力のときの試験が無い気がする"


def test_read_human_note_empty(tmp_path):
    path = tmp_path / "record.md"
    path.write_text("### 気になる点\n\n```text\n\n```\n", encoding="utf-8")

    assert fr.read_human_note(path, "気になる点") == ""


# ---------------------------------------------------------------- 変更範囲のガード


@pytest.fixture
def git_repo(tmp_path):
    """コミット済みファイルを1つ持つ一時 git リポジトリ。"""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)

    (tmp_path / "tracked.txt").write_text("original\n", encoding="utf-8")
    (tmp_path / "other.txt").write_text("other\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)

    return tmp_path


def test_snapshot_detects_modification(git_repo):
    before = fr.snapshot(git_repo)
    (git_repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    after = fr.snapshot(git_repo)

    assert fr.diff_snapshots(before, after) == ["tracked.txt"]


def test_snapshot_detects_new_untracked_file(git_repo):
    before = fr.snapshot(git_repo)
    (git_repo / "added.txt").write_text("new\n", encoding="utf-8")
    after = fr.snapshot(git_repo)

    assert fr.diff_snapshots(before, after) == ["added.txt"]


def test_snapshot_detects_deletion(git_repo):
    before = fr.snapshot(git_repo)
    (git_repo / "other.txt").unlink()
    after = fr.snapshot(git_repo)

    assert fr.diff_snapshots(before, after) == ["other.txt"]


def test_guard_ignores_preexisting_uncommitted_change(git_repo):
    """実行前から存在する未コミット変更を、今回の変更と誤認しないこと。"""
    (git_repo / "other.txt").write_text("人間が先に直した\n", encoding="utf-8")

    before = fr.snapshot(git_repo)
    (git_repo / "tracked.txt").write_text("worker が変更\n", encoding="utf-8")
    after = fr.snapshot(git_repo)

    changed = fr.diff_snapshots(before, after)

    assert changed == ["tracked.txt"]
    assert "other.txt" not in changed


def test_guard_detects_further_change_to_already_dirty_file(git_repo):
    """実行前から dirty だったファイルへの追加変更も検出すること。

    git status のパス集合だけを見る実装では、実行前後どちらも
    ` M tracked.txt` となり、この変更を検出できない。
    """
    (git_repo / "tracked.txt").write_text("人間が先に直した\n", encoding="utf-8")

    before = fr.snapshot(git_repo)
    (git_repo / "tracked.txt").write_text("人間の変更 + worker の変更\n", encoding="utf-8")
    after = fr.snapshot(git_repo)

    assert fr.diff_snapshots(before, after) == ["tracked.txt"]


def test_guard_does_not_modify_working_tree(git_repo):
    """スナップショット取得が、作業ツリーを変更しないこと。"""
    (git_repo / "tracked.txt").write_text("未コミットの変更\n", encoding="utf-8")

    fr.snapshot(git_repo)
    fr.snapshot(git_repo)

    assert (git_repo / "tracked.txt").read_text(encoding="utf-8") == "未コミットの変更\n"

    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=git_repo, capture_output=True, text=True
    )
    assert " M tracked.txt" in status.stdout


def test_is_allowed_matches_directory_prefix():
    allowed = ["docs/demo_app/features/demo/gates/"]

    assert fr.is_allowed("docs/demo_app/features/demo/gates/0001_x_g0.md", allowed) is True
    assert fr.is_allowed("docs/demo_app/features/demo/20_spec.md", allowed) is False


def test_is_allowed_matches_exact_path():
    allowed = ["docs/demo_app/features/demo/21_design.md"]

    assert fr.is_allowed("docs/demo_app/features/demo/21_design.md", allowed) is True
    assert fr.is_allowed("docs/demo_app/features/demo/21_design.md.bak", allowed) is False


def test_check_guard_reports_out_of_scope_paths():
    allowed = ["docs/demo_app/features/demo/21_design.md"]
    changed = [
        "docs/demo_app/features/demo/21_design.md",
        "docs/demo_app/features/demo/20_spec.md",
        "docs/rules/core/20_approval_and_review.md",
    ]

    assert fr.check_guard(changed, allowed) == [
        "docs/demo_app/features/demo/20_spec.md",
        "docs/rules/core/20_approval_and_review.md",
    ]


def test_check_guard_passes_when_all_allowed():
    allowed = ["src/demo_app/features/", "tests/demo_app/"]
    changed = ["src/demo_app/features/demo.py", "tests/demo_app/features/test_demo.py"]

    assert fr.check_guard(changed, allowed) == []


# ---------------------------------------------------------------- stage × role


def test_expand_replaces_placeholders():
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}
    result = fr.expand("{feature_dir}/21_design.md, src/{app}/features/", ctx)

    assert result == ["docs/demo_app/features/demo/21_design.md", "src/demo_app/features/"]


def test_stage_role_scopes_differ_at_cp3():
    """CP3 では Worker と Reviewer の変更範囲が異なること。"""
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}

    worker = fr.expand(config["stage_cp3_worker"], ctx)
    reviewer = fr.expand(config["stage_cp3_reviewer"], ctx)

    # Worker は実装とテスト。Gate記録もレビュー結果も触らない
    assert "src/demo_app/features/" in worker
    assert "tests/demo_app/" in worker
    assert not any("gates" in path for path in worker)
    assert not any("25_review_result" in path for path in worker)

    # Reviewer は Gate記録とレビュー結果。実装もテストも触らない
    assert "docs/demo_app/features/demo/gates/" in reviewer
    assert "docs/demo_app/features/demo/25_review_result.md" in reviewer
    assert not any(path.startswith("src/") for path in reviewer)
    assert not any(path.startswith("tests/") for path in reviewer)


@pytest.mark.parametrize("stage", ["g0", "cp1", "g2"])
def test_reviewer_scope_is_gates_only_before_cp3(stage):
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}

    reviewer = fr.expand(config[f"stage_{stage}_reviewer"], ctx)

    assert reviewer == ["docs/demo_app/features/demo/gates/"]


@pytest.mark.parametrize(
    ("stage", "baseline"),
    [
        ("cp1", "docs/demo_app/features/demo/20_spec.md"),
        ("g2", "docs/demo_app/features/demo/21_design.md"),
        ("cp3", "docs/demo_app/features/demo/23_test_plan.md"),
    ],
)
def test_worker_scope_excludes_baseline(stage, baseline):
    """baseline 化済みの成果物が、Worker の変更範囲に含まれないこと。"""
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}

    worker = fr.expand(config[f"stage_{stage}_worker"], ctx)

    assert fr.is_allowed(baseline, worker) is False


def test_worker_scope_never_includes_gates():
    """どの stage でも、Worker が Gate記録を変更できないこと。"""
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}

    for stage in ("g0", "cp1", "g2", "cp3"):
        worker = fr.expand(config[f"stage_{stage}_worker"], ctx)
        record = "docs/demo_app/features/demo/gates/0001_x_g0.md"

        assert fr.is_allowed(record, worker) is False, f"stage={stage}"


# ---------------------------------------------------------------- モデル解決


def test_resolve_model_maps_role_to_actual_model():
    config = {"role_build": "cheap", "model_cheap": "model-a"}

    assert fr.resolve_model(config, "build", {}) == ("cheap", "model-a")


def test_resolve_model_applies_override():
    config = {"role_design": "standard", "model_standard": "model-b", "model_strong": "model-c"}

    assert fr.resolve_model(config, "design", {"design": "strong"}) == ("strong", "model-c")


def test_resolve_model_defaults_match_cost_intent():
    """既定は design=standard / build=cheap / review=standard であること。"""
    config = fr.read_config(REPO_ROOT)

    assert config["role_design"] == "standard"
    assert config["role_build"] == "cheap"
    assert config["role_review"] == "standard"


def test_rule_document_contains_no_vendor_model_names():
    """ルール文書へ実モデル名を埋め込まないこと。"""
    text = (REPO_ROOT / fr.CONFIG_DOC).read_text(encoding="utf-8").lower()

    for name in ("claude-", "gpt-4", "gpt-5", "sonnet", "haiku", "opus", "gemini"):
        assert name not in text, f"ルール文書にモデル名が含まれています: {name}"


# ---------------------------------------------------------------- argv 組み立て


def test_build_argv_substitutes_placeholders():
    config = {"ai_command": "some-cli,-p,{instruction},--model,{model}"}
    argv = fr.build_argv(config, "指示文", "model-a")

    assert argv == ["some-cli", "-p", "指示文", "--model", "model-a"]


def test_build_argv_keeps_instruction_as_single_argument():
    """指示文にカンマや改行が含まれても、1引数のまま渡ること。"""
    config = {"ai_command": "some-cli,-p,{instruction}"}
    argv = fr.build_argv(config, "stage: CP1, mode: create\n対象: docs/a/b", "m")

    assert len(argv) == 3
    assert argv[2] == "stage: CP1, mode: create\n対象: docs/a/b"


def test_build_argv_rejects_placeholder_config():
    with pytest.raises(SystemExit):
        fr.build_argv({"ai_command": "<記入してください>"}, "指示", "m")


def test_is_placeholder():
    assert fr.is_placeholder("<記入してください>") is True
    assert fr.is_placeholder("") is True
    assert fr.is_placeholder("claude,-p,{instruction}") is False


# ---------------------------------------------------------------- ループの動作（AI は擬似）


SANDBOX_CONFIG = """```feature_loop
role_design    = standard
role_build     = cheap
role_review    = standard
model_cheap    = m-cheap
model_standard = m-standard
model_strong   = m-strong
ai_command     = fake,{instruction},{model}
stages               = G0, CP1, G2, CP3
human_gates          = CP1, CP3
max_rounds           = 3
max_returns_per_gate = 3
review_independence  = separate_context
approval_heading_cp1 = 下流進行承認
approval_heading_g2  = 実装工程進行承認
approval_heading_cp3 = 受け入れ判断
human_note_heading   = 気になる点
stage_g0_worker_role  = design
stage_cp1_worker_role = design
stage_g2_worker_role  = design
stage_cp3_worker_role = build
reviewer_role         = review
stage_g0_worker    = {feature_dir}/20_spec.md
stage_g0_reviewer  = {feature_dir}/gates/
stage_cp1_worker   = {feature_dir}/21_design.md, {feature_dir}/22_flow.md
stage_cp1_reviewer = {feature_dir}/gates/
stage_g2_worker    = {feature_dir}/23_test_plan.md, {feature_dir}/24_review_checklist.md
stage_g2_reviewer  = {feature_dir}/gates/
stage_cp3_worker   = src/{app}/features/, tests/{app}/
stage_cp3_reviewer = {feature_dir}/gates/, {feature_dir}/25_review_result.md
stage_g0_prompts   = prompts/create_feature_spec.md
stage_cp1_prompts  = prompts/create_function_design.md
stage_g2_prompts   = prompts/create_test_design.md
stage_cp3_prompts  = prompts/implement_feature.md
```
"""


@pytest.fixture
def sandbox(tmp_path):
    """git リポジトリ、設定、対象 feature を持つ一時環境。"""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)

    doc = tmp_path / fr.CONFIG_DOC
    doc.parent.mkdir(parents=True)
    doc.write_text(SANDBOX_CONFIG, encoding="utf-8")

    feature_dir = "docs/demo_app/features/demo"
    target = tmp_path / feature_dir
    target.mkdir(parents=True)

    for name in ("20_spec.md", "21_design.md", "22_flow.md", "23_test_plan.md"):
        (target / name).write_text(f"# {name}\n", encoding="utf-8")

    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)

    config = fr.read_config(tmp_path)
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": feature_dir}

    return tmp_path, config, ctx


def parse_instruction(instruction: str) -> dict[str, str]:
    fields = fr.parse_flat(instruction.split("\n", 1)[1], ":")
    fields["prompt"] = instruction.splitlines()[0]
    return fields


class FakeAI:
    """run_ai の差し替え。Reviewer 呼び出しで Gate記録を書く。"""

    def __init__(self, root, reviewer_front, side_effect=None):
        self.root = root
        self.reviewer_front = reviewer_front
        self.side_effect = side_effect
        self.calls: list[dict] = []

    def __call__(self, root, argv):
        info = parse_instruction(argv[1])
        self.calls.append(info)

        if fr.REVIEWER_PROMPT in info["prompt"]:
            record = root / info["Gate記録ファイル"]
            record.parent.mkdir(parents=True, exist_ok=True)

            front = dict(self.reviewer_front(info))
            lines = ["---"]
            lines += [f"{k}: {v}" for k, v in front.items()]
            lines += ["---", "", "# Gate記録", ""]
            record.write_text("\n".join(lines) + "\n", encoding="utf-8")

            if self.side_effect:
                self.side_effect(root)

        return 0

    def prompts_used(self) -> list[str]:
        return [call["prompt"] for call in self.calls]

    def worker_calls(self) -> list[dict]:
        return [c for c in self.calls if fr.WORKER_PROMPT in c["prompt"]]

    def reviewer_calls(self) -> list[dict]:
        return [c for c in self.calls if fr.REVIEWER_PROMPT in c["prompt"]]


def latest_front(root, ctx):
    return fr.read_front_matter(fr.latest_record(root, ctx["feature_dir"]))


def test_max_rounds_exceeded_writes_blocked_record(sandbox, monkeypatch):
    """収束しないループが、正式な BLOCKED記録を残して止まること。"""
    root, config, ctx = sandbox

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"],
        "recorded_by": "reviewer", "verdict": "IN_PROGRESS",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False)

    assert code == 1

    front = latest_front(root, ctx)
    assert front["verdict"] == "BLOCKED"
    assert front["blocked_reason"] == "non_convergence"
    assert front["recorded_by"] == "runner"


def test_max_returns_exceeded_writes_blocked_record(sandbox, monkeypatch):
    root, config, ctx = sandbox
    gates = root / ctx["feature_dir"] / "gates"

    for seq in (1, 2, 3):
        write_record(gates, f"000{seq}_x_cp3.md", verdict="RETURN", gate="CP3",
                     run_seq=seq, return_to="G2")

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False)

    assert code == 1

    front = latest_front(root, ctx)
    assert front["verdict"] == "BLOCKED"
    assert front["blocked_reason"] == "non_convergence"
    assert front["recorded_by"] == "runner"
    assert front["gate"] == "G2"


def test_reviewer_guard_violation_writes_blocked_record(sandbox, monkeypatch):
    """Reviewer が範囲外を変更したら、正式な BLOCKED記録になること。"""
    root, config, ctx = sandbox

    def touch_design(root_):
        target = root_ / ctx["feature_dir"] / "21_design.md"
        target.write_text(target.read_text(encoding="utf-8") + "reviewer が変更\n", encoding="utf-8")

    fake = FakeAI(
        root,
        lambda info: {"gate": info["stage"], "run_seq": info["run_seq"], "verdict": "PASS",
                      "next_step": "GO", "recorded_by": "reviewer"},
        side_effect=touch_design,
    )
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False)

    assert code == 1

    front = latest_front(root, ctx)
    assert front["verdict"] == "BLOCKED"
    assert front["blocked_reason"] == "guard_violation"
    assert front["recorded_by"] == "runner"
    assert "21_design.md" in fr.latest_record(root, ctx["feature_dir"]).read_text(encoding="utf-8")


def test_state_error_writes_blocked_record(sandbox, monkeypatch):
    root, config, ctx = sandbox
    write_record(root / ctx["feature_dir"] / "gates", "0001_x_cp3.md",
                 verdict="RETURN", gate="CP3", run_seq=1, return_to="G9")

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False)

    assert code == 1

    front = latest_front(root, ctx)
    assert front["verdict"] == "BLOCKED"
    assert front["blocked_reason"] == "state_error"


def test_human_note_runs_reviewer_without_worker(sandbox, monkeypatch):
    """人間コメントによる再判定で、Worker が起動しないこと。"""
    root, config, ctx = sandbox
    gates = root / ctx["feature_dir"] / "gates"

    path = write_record(gates, "0001_x_cp3.md", verdict="PASS", gate="CP3", run_seq=1)
    path.write_text(
        path.read_text(encoding="utf-8")
        + note_section("気になる点", "空入力の試験が抜けていない？"),
        encoding="utf-8",
    )

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "RETURN", "next_step": "STOP", "return_to": "G2",
        "triggered_by": info["triggered_by"],
        "triggered_by_record": info["triggered_by_record"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False)

    assert fake.worker_calls() == [], "人間コメントの再判定で Worker を起動してはいけない"
    assert len(fake.reviewer_calls()) == 1

    call = fake.reviewer_calls()[0]
    assert call["human_note"] == "空入力の試験が抜けていない？"
    assert call["triggered_by"] == "HUMAN_NOTE"
    assert call["triggered_by_record"].endswith("0001_x_cp3.md")

    front = latest_front(root, ctx)
    assert front["verdict"] == "RETURN"
    assert front["return_to"] == "G2"


def test_review_current_skips_worker(sandbox, monkeypatch):
    """--review-current で Worker を再実行せず、現在の成果物をレビューすること。"""
    root, config, ctx = sandbox

    path = write_record(root / ctx["feature_dir"] / "gates", "0001_x_cp1.md",
                        verdict="PASS", gate="CP1", run_seq=1)
    path.write_text(path.read_text(encoding="utf-8") + approval("下流進行承認", True),
                    encoding="utf-8")

    # 人間が手で 23_test_plan.md を修正した状態
    plan = root / ctx["feature_dir"] / "23_test_plan.md"
    plan.write_text("# 人間が直したテスト計画\n", encoding="utf-8")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO", "mode": info["mode"],
        "triggered_by": info["triggered_by"], "supersedes": info["supersedes"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False, review_current="G2")

    assert code == 0
    assert fake.worker_calls() == [], "--review-current で Worker を起動してはいけない"
    assert len(fake.reviewer_calls()) == 1
    assert fake.reviewer_calls()[0]["mode"] == "manual"

    # 人間の修正が残っていること
    assert plan.read_text(encoding="utf-8") == "# 人間が直したテスト計画\n"

    front = latest_front(root, ctx)
    assert front["gate"] == "G2"
    assert front["mode"] == "manual"
    assert front["triggered_by"] == "MANUAL"


def test_review_current_returns_to_auto_mode(sandbox, monkeypatch):
    """--review-current の後、通常のオートモードへ戻れること。"""
    root, config, ctx = sandbox

    path = write_record(root / ctx["feature_dir"] / "gates", "0001_x_cp1.md",
                        verdict="PASS", gate="CP1", run_seq=1)
    path.write_text(path.read_text(encoding="utf-8") + approval("下流進行承認", True),
                    encoding="utf-8")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO", "mode": info["mode"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False, review_current="G2")

    action = fr.resolve_action(root, config, ctx["feature_dir"])

    assert (action.kind, action.stage) == ("run", "CP3")


def test_review_current_rejects_unknown_stage(sandbox):
    root, config, ctx = sandbox

    with pytest.raises(SystemExit):
        fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False, review_current="G9")


def test_normal_run_invokes_worker_then_reviewer(sandbox, monkeypatch):
    """通常実行では Worker → Reviewer の順に、別プロセスで起動されること。"""
    root, config, ctx = sandbox

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False)

    assert fake.prompts_used() == [
        f"{fr.WORKER_PROMPT} を参照してください。",
        f"{fr.REVIEWER_PROMPT} を参照してください。",
    ]


def test_reviewer_receives_human_gate_flag(sandbox, monkeypatch):
    """human_gate は stage 名ではなく設定から Reviewer へ渡ること。"""
    root, config, ctx = sandbox
    g2_config = dict(config, human_gates="CP1, G2, CP3")

    write_record(root / ctx["feature_dir"] / "gates", "0001_x_cp1.md",
                 verdict="PASS", gate="CP1", run_seq=1)
    path = fr.latest_record(root, ctx["feature_dir"])
    path.write_text(path.read_text(encoding="utf-8") + approval("下流進行承認", True),
                    encoding="utf-8")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, g2_config, ctx, {}, once=True, dry_run=False)

    assert fake.reviewer_calls()[0]["human_gate"] == "yes"


def test_worker_receives_cheap_model_at_cp3(sandbox, monkeypatch):
    """CP3 の Worker に build ロール（既定 cheap）が割り当たること。"""
    root, config, ctx = sandbox
    gates = root / ctx["feature_dir"] / "gates"

    path = write_record(gates, "0001_x_g2.md", verdict="PASS", gate="G2", run_seq=1)
    path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False)

    worker = fake.worker_calls()[0]
    assert worker["stage"] == "CP3"
    assert worker["使用モデル区分"] == "cheap"
    assert fake.reviewer_calls()[0]["使用モデル区分"] == "standard"


def test_resolve_model_treats_placeholder_as_unset():
    config = {"role_build": "cheap", "model_cheap": "<記入してください>"}

    assert fr.resolve_model(config, "build", {}) == ("cheap", "")


# ---------------------------------------------------------------- 設定とテンプレートの整合


@pytest.mark.parametrize(
    "key", ["approval_heading_cp1", "approval_heading_cp3", "human_note_heading"]
)
def test_config_headings_exist_in_gate_record_template(key):
    """runner が読む見出しが、Gate記録テンプレートに存在すること。

    どちらかだけを変更すると、承認検出と自然文の読み取りが黙って壊れる。
    """
    import re

    config = fr.read_config(REPO_ROOT)
    template = (REPO_ROOT / "docs/templates/gate_record_template.md").read_text(encoding="utf-8")
    heading = config[key]

    assert re.search(rf"^#{{2,3}}\s*{re.escape(heading)}\s*$", template, re.MULTILINE), (
        f"{key}={heading!r} が gate_record_template.md に見つかりません"
    )


def test_config_stages_have_role_and_scope_entries():
    """stages に列挙した全 stage に、role と stage × role の範囲が定義されていること。"""
    config = fr.read_config(REPO_ROOT)

    for stage in fr.split_list(config["stages"]):
        key = stage.lower()

        assert f"stage_{key}_worker" in config, stage
        assert f"stage_{key}_reviewer" in config, stage
        assert f"stage_{key}_worker_role" in config, stage
        assert f"stage_{key}_prompts" in config, stage


def test_human_gates_are_subset_of_stages():
    config = fr.read_config(REPO_ROOT)
    stages = set(fr.split_list(config["stages"]))

    for gate in fr.split_list(config["human_gates"]):
        assert gate in stages, gate


def test_every_human_gate_has_approval_heading():
    config = fr.read_config(REPO_ROOT)

    for gate in fr.split_list(config["human_gates"]):
        key = f"approval_heading_{gate.lower()}"
        assert config.get(key), f"{gate} に {key} がありません"


def test_g2_can_be_promoted_to_human_gate():
    """安全弁（human_gates に G2 を追加）が実際に成立すること。

    承認見出しと、Gate記録テンプレートの承認欄の両方が必要。
    """
    import re

    config = fr.read_config(REPO_ROOT)
    heading = config.get("approval_heading_g2", "")

    assert heading, "approval_heading_g2 がありません"

    template = (REPO_ROOT / "docs/templates/gate_record_template.md").read_text(encoding="utf-8")

    assert re.search(rf"^#{{2,3}}\s*{re.escape(heading)}\s*$", template, re.MULTILINE), (
        "G2 の承認欄が gate_record_template.md にありません"
    )


# ---------------------------------------------------------------- 人間コメントからの再判定


def approval(heading: str, checked: bool) -> str:
    mark = "x" if checked else " "
    return f"\n### {heading}\n\n- [{mark}] 回答した\n- [{mark}] 承認する\n"


def note_section(heading: str, text: str) -> str:
    return f"\n### {heading}\n\n```text\n{text}\n```\n"


CONFIG_NOTE = dict(CONFIG, human_note_heading="気になる点")


def test_human_note_triggers_review_before_approval(feature):
    """CP3 PASS のあと人間コメントを書くと、承認待ちより先に Reviewer が起動すること。"""
    root, feature_dir = feature
    path = write_record(root / feature_dir / "gates", "0006_x_cp3.md", verdict="PASS", gate="CP3")
    path.write_text(
        path.read_text(encoding="utf-8")
        + note_section("気になる点", "空入力のときの試験が抜けていない？"),
        encoding="utf-8",
    )

    action = fr.resolve_action(root, CONFIG_NOTE, feature_dir)

    assert action.kind == "review_note"
    assert action.stage == "CP3"
    assert action.note == "空入力のときの試験が抜けていない？"


def test_human_note_takes_precedence_over_approval(feature):
    """承認済みでも、未処理コメントがあれば先に再レビューすること。"""
    root, feature_dir = feature
    path = write_record(root / feature_dir / "gates", "0006_x_cp3.md", verdict="PASS", gate="CP3")
    path.write_text(
        path.read_text(encoding="utf-8")
        + approval("受け入れ判断", True)
        + note_section("気になる点", "異常系が足りない気がする"),
        encoding="utf-8",
    )

    assert fr.resolve_action(root, CONFIG_NOTE, feature_dir).kind == "review_note"


def test_processed_human_note_is_not_handled_twice(feature):
    """後続記録が参照しているコメントは、再実行しても再処理されないこと。"""
    root, feature_dir = feature
    gates = root / feature_dir / "gates"

    path = write_record(gates, "0006_x_cp3.md", verdict="PASS", gate="CP3")
    path.write_text(
        path.read_text(encoding="utf-8") + note_section("気になる点", "異常系が足りない"),
        encoding="utf-8",
    )

    # コメントを処理した結果の記録
    write_record(
        gates, "0007_x_cp3.md", verdict="PASS", gate="CP3",
        triggered_by="HUMAN_NOTE", triggered_by_record="gates/0006_x_cp3.md",
    )

    assert fr.is_note_processed(root, feature_dir, gates / "0006_x_cp3.md") is True

    # 最新は 0007。未承認なので承認待ちへ進む（再レビューではない）
    assert fr.resolve_action(root, CONFIG_NOTE, feature_dir).kind == "await_human"


def test_human_note_can_produce_return(feature):
    """人間コメントから RETURN(G2) が生成された状態を、runner が正しく解決すること。"""
    root, feature_dir = feature
    gates = root / feature_dir / "gates"

    src = write_record(gates, "0006_x_cp3.md", verdict="PASS", gate="CP3")
    src.write_text(
        src.read_text(encoding="utf-8") + note_section("気になる点", "空入力の試験が無い"),
        encoding="utf-8",
    )
    write_record(
        gates, "0007_x_cp3.md", verdict="RETURN", gate="CP3", return_to="G2",
        triggered_by="HUMAN_NOTE", triggered_by_record="gates/0006_x_cp3.md",
    )

    action = fr.resolve_action(root, CONFIG_NOTE, feature_dir)

    assert (action.kind, action.stage) == ("run", "G2")
    assert action.record.name == "0007_x_cp3.md"


def test_causality_for_review_note(feature):
    root, feature_dir = feature
    previous = write_record(root / feature_dir / "gates", "0006_x_cp3.md",
                            verdict="PASS", gate="CP3")

    causality = fr.compute_causality(root, feature_dir, "CP3", previous, "review_note")

    assert causality["triggered_by"] == "HUMAN_NOTE"
    assert causality["triggered_by_record"].endswith("0006_x_cp3.md")


def test_causality_for_review_only(feature):
    """マニュアル介入からの復帰は MANUAL として記録されること。"""
    root, feature_dir = feature
    gates = root / feature_dir / "gates"

    write_record(gates, "0003_x_g2.md", verdict="PASS", gate="G2")
    previous = write_record(gates, "0004_x_cp3.md", verdict="PASS", gate="CP3")

    causality = fr.compute_causality(root, feature_dir, "G2", previous, "review_only")

    assert causality["triggered_by"] == "MANUAL"
    assert causality["supersedes"].endswith("0003_x_g2.md")


# ---------------------------------------------------------------- runner による BLOCKED記録


CTX = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}


def test_write_runner_record_creates_blocked_record(feature):
    root, feature_dir = feature
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": feature_dir}

    record = fr.write_runner_record(
        root, ctx, "G2", "guard_violation", "Reviewer が範囲外を変更しました。",
        None, ["docs/demo_app/features/demo/21_design.md"],
    )

    front = fr.read_front_matter(record)

    assert front["verdict"] == "BLOCKED"
    assert front["next_step"] == "STOP"
    assert front["blocked_reason"] == "guard_violation"
    assert front["recorded_by"] == "runner"
    assert front["gate"] == "G2"
    assert front["guard_violations"] == "1"
    assert "21_design.md" in record.read_text(encoding="utf-8")


def test_runner_record_does_not_overwrite_existing(feature):
    """runner の BLOCKED記録が、既存の確定記録を書き換えないこと。"""
    root, feature_dir = feature
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": feature_dir}
    gates = root / feature_dir / "gates"

    existing = write_record(gates, "0001_x_g2.md", verdict="PASS", gate="G2")
    before = existing.read_text(encoding="utf-8")

    record = fr.write_runner_record(root, ctx, "G2", "non_convergence", "上限に達しました。", existing)

    assert existing.read_text(encoding="utf-8") == before
    assert record != existing
    assert len(fr.list_records(root, feature_dir)) == 2


def test_runner_record_is_readable_as_next_state(feature):
    """runner が書いた BLOCKED記録を、次の実行が停止状態として解決できること。"""
    root, feature_dir = feature
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": feature_dir}

    fr.write_runner_record(root, ctx, "CP1", "state_error", "状態を解決できません。", None)

    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert action.kind == "stop"
    assert action.note == "state_error"


def test_invalid_verdict_becomes_error_action(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0001_x_g0.md", verdict="WEIRD", gate="G0")

    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert action.kind == "error"


def test_invalid_return_target_becomes_error_action(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0001_x_cp3.md",
                 verdict="RETURN", gate="CP3", return_to="G9")

    assert fr.resolve_action(root, CONFIG, feature_dir).kind == "error"


def test_missing_approval_heading_becomes_error_action(feature):
    """human_gates に入れたのに承認見出しが無い場合、黙って通さないこと。"""
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0003_x_g2.md", verdict="PASS", gate="G2")

    broken = dict(CONFIG, human_gates="CP1, G2, CP3")  # approval_heading_g2 がない

    action = fr.resolve_action(root, broken, feature_dir)

    assert action.kind == "error"
    assert "approval_heading_g2" in action.note


# ---------------------------------------------------------------- G2 を Human Gate にする


G2_CONFIG = dict(
    CONFIG,
    human_gates="CP1, G2, CP3",
    approval_heading_g2="実装工程進行承認",
    human_note_heading="気になる点",
)


def test_g2_stops_when_configured_as_human_gate(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0003_x_g2.md", verdict="PASS", gate="G2")

    assert fr.resolve_action(root, G2_CONFIG, feature_dir).kind == "await_human"


def test_g2_resumes_after_approval(feature):
    root, feature_dir = feature
    path = write_record(root / feature_dir / "gates", "0003_x_g2.md", verdict="PASS", gate="G2")
    path.write_text(
        path.read_text(encoding="utf-8") + approval("実装工程進行承認", True),
        encoding="utf-8",
    )

    action = fr.resolve_action(root, G2_CONFIG, feature_dir)

    assert (action.kind, action.stage) == ("run", "CP3")


def test_g2_remains_ai_gate_by_default(feature):
    """既定設定では G2 で人間を止めないこと。"""
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0003_x_g2.md", verdict="PASS", gate="G2")

    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert (action.kind, action.stage) == ("run", "CP3")

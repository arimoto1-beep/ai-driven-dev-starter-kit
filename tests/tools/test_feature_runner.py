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

    assert config["stages"] == "CP1, G1, G2, CP3"
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
    path = write_record(tmp_path, "0001_x_cp1.md", verdict="PASS", gate="CP1", return_to="")
    front = fr.read_front_matter(path)

    assert front["verdict"] == "PASS"
    assert front["gate"] == "CP1"
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
    write_record(gates, "0002_20260101T000000_g1.md", verdict="PASS", gate="G1")

    names = [p.name for p in fr.list_records(root, feature_dir)]
    assert names == ["0002_20260101T000000_g1.md", "0010_20260101T000000_g2.md"]


def test_next_seq_increments(feature):
    root, feature_dir = feature
    assert fr.next_seq(root, feature_dir) == 1

    write_record(root / feature_dir / "gates", "0007_x_cp1.md", verdict="PASS", gate="CP1")
    assert fr.next_seq(root, feature_dir) == 8


def test_new_record_path_does_not_overwrite(feature):
    root, feature_dir = feature
    first = fr.new_record_path(root, feature_dir, "G1")
    first.write_text("既存", encoding="utf-8")

    # 同じ連番・同じ秒でも、既存ファイルを潰さない名前になること
    monkey = fr.new_record_path(root, feature_dir, "G1")
    assert monkey != first


# ---------------------------------------------------------------- 状態解決


CONFIG = {
    "stages": "CP1, G1, G2, CP3",
    "human_gates": "CP1, CP3",
    "approval_heading_cp1": "仕様承認",
    "approval_heading_cp3": "受け入れ判断",
}


def test_resolve_action_starts_at_first_stage(feature):
    root, feature_dir = feature
    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert action.kind == "run"
    assert action.stage == "CP1"


def test_resolve_action_advances_after_ai_gate_pass(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0002_x_g1.md", verdict="PASS", gate="G1")

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert (action.kind, action.stage) == ("run", "G2")


def test_resolve_action_waits_for_human_at_human_gate(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0001_x_cp1.md", verdict="PASS", gate="CP1")

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert action.kind == "await_human"


def test_resolve_action_continues_after_human_approval(feature):
    root, feature_dir = feature
    path = write_record(root / feature_dir / "gates", "0001_x_cp1.md", verdict="PASS", gate="CP1")
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n### 仕様承認\n\n- [x] 回答した\n- [x] 承認する\n",
        encoding="utf-8",
    )

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert (action.kind, action.stage) == ("run", "G1")


def test_resolve_action_resumes_in_progress_as_fix(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0002_x_g1.md", verdict="IN_PROGRESS", gate="G1")

    action = fr.resolve_action(root, CONFIG, feature_dir)
    assert (action.kind, action.stage) == ("fix", "G1")


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
        "0001_x_cp1.md",
        verdict="BLOCKED",
        gate="CP1",
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
    write_record(gates, "0003_x_cp3.md", verdict="RETURN", gate="CP3", return_to="G1")

    assert fr.count_returns_to(root, feature_dir, "G2") == 2
    assert fr.count_returns_to(root, feature_dir, "G1") == 1


# ---------------------------------------------------------------- 人間確認欄


def test_is_approved_requires_all_boxes_checked(tmp_path):
    path = tmp_path / "record.md"
    path.write_text("### 仕様承認\n\n- [x] A\n- [ ] B\n", encoding="utf-8")

    assert fr.is_approved(path, "仕様承認") is False


def test_is_approved_ignores_unchecked_options_outside_section(tmp_path):
    """「判断してほしいこと」の排他選択肢は未チェックが残るが、承認判定に影響しないこと。"""
    path = tmp_path / "record.md"
    path.write_text(
        "### 判断してほしいこと\n\n- [x] AI案で確定\n- [ ] 別案で確定\n\n"
        "### 仕様承認\n\n- [x] 回答した\n- [x] 承認する\n",
        encoding="utf-8",
    )

    assert fr.is_approved(path, "仕様承認") is True


def test_is_approved_false_when_section_missing(tmp_path):
    path = tmp_path / "record.md"
    path.write_text("### 別の見出し\n\n- [x] A\n", encoding="utf-8")

    assert fr.is_approved(path, "仕様承認") is False


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

    assert fr.is_allowed("docs/demo_app/features/demo/gates/0001_x_cp1.md", allowed) is True
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


@pytest.mark.parametrize("stage", ["cp1", "g1", "g2"])
def test_reviewer_scope_is_gates_only_before_cp3(stage):
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}

    reviewer = fr.expand(config[f"stage_{stage}_reviewer"], ctx)

    assert reviewer == ["docs/demo_app/features/demo/gates/"]


@pytest.mark.parametrize(
    ("stage", "baseline"),
    [
        ("g1", "docs/demo_app/features/demo/20_spec.md"),
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

    for stage in ("cp1", "g1", "g2", "cp3"):
        worker = fr.expand(config[f"stage_{stage}_worker"], ctx)
        record = "docs/demo_app/features/demo/gates/0001_x_cp1.md"

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
    argv = fr.build_argv(config, "stage: G1, mode: create\n対象: docs/a/b", "m")

    assert len(argv) == 3
    assert argv[2] == "stage: G1, mode: create\n対象: docs/a/b"


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
stages               = CP1, G1, G2, CP3
human_gates          = CP1, CP3
spec_stage           = CP1
spec_artifact        = {feature_dir}/20_spec.md
max_rounds           = 3
max_returns_per_gate = 3
review_independence  = separate_context
approval_heading_cp1 = 仕様承認
approval_heading_g1  = 設計進行承認
approval_heading_g2  = 実装工程進行承認
approval_heading_cp3 = 受け入れ判断
human_note_heading   = 気になる点
stage_cp1_worker_role  = design
stage_g1_worker_role = design
stage_g2_worker_role  = design
stage_cp3_worker_role = build
reviewer_role         = review
stage_cp1_worker    = {feature_dir}/20_spec.md
stage_cp1_reviewer  = {feature_dir}/gates/
stage_g1_worker   = {feature_dir}/21_design.md, {feature_dir}/22_flow.md
stage_g1_reviewer = {feature_dir}/gates/
stage_g2_worker    = {feature_dir}/23_test_plan.md, {feature_dir}/24_review_checklist.md
stage_g2_reviewer  = {feature_dir}/gates/
stage_cp3_worker   = src/{app}/features/, tests/{app}/
stage_cp3_reviewer = {feature_dir}/gates/, {feature_dir}/25_review_result.md
stage_g1_artifacts  = {feature_dir}/21_design.md, {feature_dir}/22_flow.md
stage_g2_artifacts  = {feature_dir}/23_test_plan.md
stage_cp3_artifacts = src/{app}/features/{feature}.py
stage_cp1_prompts   = prompts/create_feature_spec.md
stage_g1_prompts  = prompts/create_function_design.md
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


def approve_spec(root, config, ctx, name="0001_x_cp1.md", seq=1):
    """承認済みの仕様 baseline（CP1 記録）を作る。製造 stage のテスト前提。"""
    target = fr.spec_path(root, config, ctx)
    record = write_record(
        root / ctx["feature_dir"] / "gates", name,
        verdict="PASS", next_step="GO", gate="CP1", run_seq=seq,
        recorded_by="reviewer", spec_hash=fr.file_hash(target),
    )
    record.write_text(
        record.read_text(encoding="utf-8") + approval("仕様承認", True),
        encoding="utf-8",
    )
    return record


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

    path = write_record(root / ctx["feature_dir"] / "gates", "0001_x_g1.md",
                        verdict="PASS", gate="G1", run_seq=1)
    path.write_text(path.read_text(encoding="utf-8") + approval("仕様承認", True),
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

    path = write_record(root / ctx["feature_dir"] / "gates", "0001_x_g1.md",
                        verdict="PASS", gate="G1", run_seq=1)
    path.write_text(path.read_text(encoding="utf-8") + approval("仕様承認", True),
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
    g1_config = dict(config, human_gates="CP1, G1, CP3",
                     approval_heading_g1="設計進行承認")

    approve_spec(root, config, ctx)

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, g1_config, ctx, {}, once=True, dry_run=False)

    assert fake.reviewer_calls()[0]["stage"] == "G1"
    assert fake.reviewer_calls()[0]["human_gate"] == "yes"


# ---------------------------------------------------------------- 仕様 baseline の境界


def test_spec_stage_is_first_and_human_gate():
    """CP1 が最初の stage であり、Human Gate であること（製造への入口）。"""
    config = fr.read_config(REPO_ROOT)

    stages = fr.split_list(config["stages"])
    human_gates = fr.split_list(config["human_gates"])

    assert stages[0] == "CP1"
    assert config["spec_stage"] == "CP1"
    assert "CP1" in human_gates, "CP1 を Human Gate から外すと承認なしで製造が始まる"


def test_manufacturing_stages_are_after_spec_stage():
    config = fr.read_config(REPO_ROOT)

    assert fr.is_manufacturing_stage(config, "CP1") is False
    assert fr.is_manufacturing_stage(config, "G1") is True
    assert fr.is_manufacturing_stage(config, "G2") is True
    assert fr.is_manufacturing_stage(config, "CP3") is True


def test_spec_is_not_writable_from_manufacturing_stages():
    """9. 承認済み仕様が、製造 stage の変更範囲に含まれないこと。"""
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo", "feature_dir": "docs/demo_app/features/demo"}
    spec = "docs/demo_app/features/demo/20_spec.md"

    # 仕様工程の Worker だけが 20_spec.md を書ける
    assert fr.is_allowed(spec, fr.expand(config["stage_cp1_worker"], ctx)) is True

    for stage in ("g1", "g2", "cp3"):
        worker = fr.expand(config[f"stage_{stage}_worker"], ctx)
        reviewer = fr.expand(config[f"stage_{stage}_reviewer"], ctx)

        assert fr.is_allowed(spec, worker) is False, f"stage={stage} の Worker"
        assert fr.is_allowed(spec, reviewer) is False, f"stage={stage} の Reviewer"


def test_spec_review_runs_reviewer_only(sandbox, monkeypatch):
    """1. 仕様レビューを単独実行でき、Worker が起動しないこと。"""
    root, config, ctx = sandbox

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO", "spec_hash": info["spec_hash"],
        "mode": info["mode"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False, spec_review=True)

    assert code == 0
    assert fake.worker_calls() == [], "仕様レビューで Worker を起動してはいけない"
    assert len(fake.reviewer_calls()) == 1
    assert fake.reviewer_calls()[0]["stage"] == "CP1"

    front = latest_front(root, ctx)
    assert front["gate"] == "CP1"
    assert front["spec_hash"] == fr.file_hash(fr.spec_path(root, config, ctx))


def test_spec_review_can_run_repeatedly(sandbox, monkeypatch):
    """1'. 仕様レビューを何度でも実行でき、過去の記録が残ること。"""
    root, config, ctx = sandbox

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO", "spec_hash": info["spec_hash"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    for _ in range(3):
        fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False, spec_review=True)

    records = fr.list_records(root, ctx["feature_dir"])

    assert len(records) == 3
    assert [p.name.split("_", 1)[0] for p in records] == ["0001", "0002", "0003"]


def test_spec_review_blocked_does_not_reach_manufacturing(sandbox, monkeypatch):
    """2. 仕様不足を検出した場合、製造側へ進まず人間へ返ること。"""
    root, config, ctx = sandbox

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "BLOCKED", "next_step": "STOP",
        "blocked_reason": "business_decision", "spec_hash": info["spec_hash"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False, spec_review=True)

    # 製造 stage は一度も起動していない
    assert all(call["stage"] == "CP1" for call in fake.calls)

    action = fr.resolve_action(root, config, ctx["feature_dir"])
    assert action.kind == "stop"
    assert action.note == "business_decision"


def test_spec_review_rejected_without_spec(sandbox):
    root, config, ctx = sandbox
    (root / ctx["feature_dir"] / "20_spec.md").unlink()

    with pytest.raises(SystemExit) as error:
        fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False, spec_review=True)

    assert "仕様書" in str(error.value)


def test_spec_review_is_exclusive_with_other_modes(sandbox):
    root, config, ctx = sandbox

    with pytest.raises(SystemExit):
        fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False,
                   spec_review=True, retry_blocked=True)


# ---------------------------------------------------------------- Manufacturing Preflight


def test_preflight_blocks_without_human_approval(sandbox, monkeypatch):
    """3. 仕様レビュー PASS でも、人間承認がなければ製造しないこと。"""
    root, config, ctx = sandbox

    # 承認欄が未チェックの CP1 PASS
    record = write_record(
        root / ctx["feature_dir"] / "gates", "0001_x_cp1.md",
        verdict="PASS", next_step="GO", gate="CP1", run_seq=1,
        spec_hash=fr.file_hash(fr.spec_path(root, config, ctx)),
    )
    record.write_text(
        record.read_text(encoding="utf-8") + approval("仕様承認", False),
        encoding="utf-8",
    )

    design = root / ctx["feature_dir"] / "21_design.md"
    before = design.read_text(encoding="utf-8")

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False)

    assert code == 0, "承認待ちは異常停止ではない"
    assert fake.calls == [], "承認前に製造 stage を起動してはいけない"
    assert design.read_text(encoding="utf-8") == before, "21_design.md が生成・更新されてはいけない"

    action = fr.resolve_action(root, config, ctx["feature_dir"])
    assert (action.kind, action.stage) == ("await_human", "CP1")


def test_preflight_blocks_when_spec_changed_after_approval(sandbox, monkeypatch):
    """4. 承認後に 20_spec.md が変更されたら、製造を開始しないこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)

    # 承認後に仕様を変更する
    spec = fr.spec_path(root, config, ctx)
    spec.write_text(spec.read_text(encoding="utf-8") + "\n- REQ-002: 後から追加\n", encoding="utf-8")

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False)

    assert code == 1
    assert fake.calls == [], "baseline がずれた状態で製造してはいけない"

    front = latest_front(root, ctx)
    assert front["verdict"] == "BLOCKED"
    assert front["blocked_reason"] == "spec_not_approved"
    assert front["recorded_by"] == "runner"
    assert front["gate"] == "CP1"


def test_preflight_blocks_when_approval_has_no_spec_hash(sandbox, monkeypatch):
    """spec_hash が記録されていない承認は、有効な baseline として扱わないこと。"""
    root, config, ctx = sandbox

    record = write_record(
        root / ctx["feature_dir"] / "gates", "0001_x_cp1.md",
        verdict="PASS", next_step="GO", gate="CP1", run_seq=1, spec_hash="",
    )
    record.write_text(
        record.read_text(encoding="utf-8") + approval("仕様承認", True),
        encoding="utf-8",
    )

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    assert fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False) == 1
    assert fake.calls == []


def test_preflight_passes_with_approved_matching_baseline(sandbox, monkeypatch):
    """5. 仕様レビュー PASS ＋ 人間承認 ＋ 同一 baseline なら製造へ進むこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False)

    assert code == 0
    assert fake.worker_calls()[0]["stage"] == "G1"
    assert "21_design.md" in fake.worker_calls()[0]["変更してよいファイル"]


def test_approval_does_not_need_to_be_latest_record(sandbox, monkeypatch):
    """承認は「どの仕様を承認したか」を表す。最新記録である必要はないこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx, name="0001_x_cp1.md", seq=1)

    # 仕様は変えずに、もう一度レビューだけ回す（承認欄は未チェック）
    write_record(
        root / ctx["feature_dir"] / "gates", "0002_x_cp1.md",
        verdict="PASS", next_step="GO", gate="CP1", run_seq=2,
        spec_hash=fr.file_hash(fr.spec_path(root, config, ctx)),
    )

    ok, detail = fr.check_spec_baseline(root, config, ctx)

    assert ok, detail


def test_preflight_accepts_older_approval_when_current_hash_matches(sandbox):
    """A承認→B承認→Aへ戻した場合、内容一致する過去のA承認を利用できること。"""
    root, config, ctx = sandbox
    spec = fr.spec_path(root, config, ctx)

    original = spec.read_text(encoding="utf-8")
    approval_a = approve_spec(root, config, ctx, name="0001_x_cp1.md", seq=1)

    spec.write_text(original + "\n- REQ-002: Bだけの要求\n", encoding="utf-8")
    approve_spec(root, config, ctx, name="0002_x_cp1.md", seq=2)

    # 現在の仕様をAへ戻す。最新承認Bではなく、過去のA承認が一致する。
    spec.write_text(original, encoding="utf-8")

    matched, front = fr.find_spec_approval(
        root, config, ctx["feature_dir"], required_spec_hash=fr.file_hash(spec),
    )
    ok, detail = fr.check_spec_baseline(root, config, ctx)

    assert matched == approval_a
    assert front["spec_hash"] == fr.file_hash(spec)
    assert ok, detail


def test_check_spec_baseline_reports_reason(sandbox):
    root, config, ctx = sandbox

    ok, detail = fr.check_spec_baseline(root, config, ctx)

    assert ok is False
    assert "仕様承認" in detail


def test_reviewer_receives_spec_hash_only_at_spec_stage(sandbox):
    root, config, ctx = sandbox

    assert fr.current_spec_hash(root, config, ctx, "CP1") != ""
    assert fr.current_spec_hash(root, config, ctx, "G1") == ""
    assert fr.current_spec_hash(root, config, ctx, "CP3") == ""


def test_spec_hash_changes_with_content(sandbox):
    root, config, ctx = sandbox
    spec = fr.spec_path(root, config, ctx)

    before = fr.file_hash(spec)
    spec.write_text(spec.read_text(encoding="utf-8") + "追記\n", encoding="utf-8")

    assert fr.file_hash(spec) != before


# ---------------------------------------------------------------- 製造開始後の仕様不足


def test_return_to_spec_stage_waits_for_reapproval(sandbox, monkeypatch):
    """6. 製造中の仕様不足は RETURN(CP1) となり、人間の再承認まで進まないこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)

    # G1 が「仕様が沈黙している」と判断して差し戻す
    write_record(
        root / ctx["feature_dir"] / "gates", "0002_x_g1.md",
        verdict="RETURN", next_step="STOP", gate="G1", run_seq=2, return_to="CP1",
    )

    action = fr.resolve_action(root, config, ctx["feature_dir"])
    assert (action.kind, action.stage) == ("run", "CP1")

    # CP1 を再実行しても、承認欄が未チェックのうちは製造へ戻らない
    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO", "spec_hash": info["spec_hash"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False)

    after = fr.resolve_action(root, config, ctx["feature_dir"])
    assert (after.kind, after.stage) == ("await_human", "CP1")


def test_manufacturing_worker_cannot_touch_approved_spec(sandbox, monkeypatch):
    """6'. 製造 Worker が承認済み仕様を書き換えたら、ガードが検出すること。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)

    spec = fr.spec_path(root, config, ctx)

    def rewrite_spec(root_, argv):
        info = parse_instruction(argv[1])
        if fr.WORKER_PROMPT in info["prompt"]:
            spec.write_text("AIが勝手に補完した仕様\n", encoding="utf-8")
        else:
            record = root_ / info["Gate記録ファイル"]
            record.parent.mkdir(parents=True, exist_ok=True)
            record.write_text(
                "---\ngate: G1\nrun_seq: 2\nverdict: PASS\nnext_step: GO\n"
                f"guard_violations: {info['guard_violations']}\n---\n\n# Gate記録\n",
                encoding="utf-8",
            )
        return 0

    monkeypatch.setattr(fr, "run_ai", rewrite_spec)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False)

    # Reviewer へ違反として渡っている
    front = latest_front(root, ctx)
    assert "20_spec.md" in front["guard_violations"]


# ---------------------------------------------------------------- BLOCKED からの再試行


def blocked_record(root, feature_dir, name="0001_x_cp1.md", stage="CP1",
                   reason="state_error", seq=1):
    return write_record(
        root / feature_dir / "gates", name,
        verdict="BLOCKED", next_step="STOP", gate=stage, run_seq=seq,
        recorded_by="runner", blocked_reason=reason,
    )


def test_blocked_still_stops_without_retry_flag(feature):
    """1. 通常実行では、これまでどおり BLOCKED で停止すること。"""
    root, feature_dir = feature
    blocked_record(root, feature_dir)

    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert action.kind == "stop"
    assert action.note == "state_error"


def test_normal_run_does_not_auto_resume_from_blocked(sandbox, monkeypatch):
    """1'. --retry-blocked なしの実行が、BLOCKED を自動で無視しないこと。"""
    root, config, ctx = sandbox
    blocked_record(root, ctx["feature_dir"])

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False)

    assert code == 1
    assert fake.calls == [], "BLOCKED のまま AI を起動してはいけない"
    assert len(fr.list_records(root, ctx["feature_dir"])) == 1


def test_resolve_retry_action_targets_blocked_stage(feature):
    """2. 最新が BLOCKED なら、その stage の再試行を組み立てること。"""
    root, feature_dir = feature
    record = blocked_record(root, feature_dir, stage="CP1")

    action = fr.resolve_retry_action(root, CONFIG, feature_dir)

    assert action.kind == "retry"
    assert action.stage == "CP1"
    assert action.record == record
    assert action.note == "state_error"


def test_retry_blocked_reruns_worker_and_reviewer(sandbox, monkeypatch):
    """2. --retry-blocked で Worker / Reviewer を再実行できること。"""
    root, config, ctx = sandbox
    blocked_record(root, ctx["feature_dir"], stage="CP1")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
        "triggered_by": info["triggered_by"],
        "triggered_by_record": info["triggered_by_record"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False, retry_blocked=True)

    assert code == 0
    assert len(fake.worker_calls()) == 1
    assert len(fake.reviewer_calls()) == 1
    assert fake.worker_calls()[0]["stage"] == "CP1"
    assert fake.worker_calls()[0]["mode"] == "create"


def test_retry_preserves_original_blocked_record(sandbox, monkeypatch):
    """3. 過去の BLOCKED記録が変更・削除されないこと。"""
    root, config, ctx = sandbox
    original = blocked_record(root, ctx["feature_dir"], stage="CP1")
    before = original.read_text(encoding="utf-8")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False, retry_blocked=True)

    assert original.exists()
    assert original.read_text(encoding="utf-8") == before
    assert fr.read_front_matter(original)["verdict"] == "BLOCKED"


def test_retry_creates_new_record_number(sandbox, monkeypatch):
    """4. 再試行後は新しい Gate記録番号になること。"""
    root, config, ctx = sandbox
    original = blocked_record(root, ctx["feature_dir"], stage="CP1", seq=1)

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False, retry_blocked=True)

    records = fr.list_records(root, ctx["feature_dir"])

    assert len(records) == 2
    assert records[0] == original
    assert records[1].name.startswith("0002_")
    assert records[1].name.endswith("_cp1.md")


def test_retry_records_causality_to_blocked_record(sandbox, monkeypatch):
    """5. 新しい記録から、再試行元の BLOCKED記録を追跡できること。"""
    root, config, ctx = sandbox
    original = blocked_record(root, ctx["feature_dir"], stage="CP1")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
        "triggered_by": info["triggered_by"],
        "triggered_by_record": info["triggered_by_record"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False, retry_blocked=True)

    front = latest_front(root, ctx)

    assert front["triggered_by"] == "RETRY_BLOCKED"
    assert Path(front["triggered_by_record"]).name == original.name


def test_compute_causality_for_retry(feature):
    root, feature_dir = feature
    previous = blocked_record(root, feature_dir, stage="G1")

    causality = fr.compute_causality(root, feature_dir, "G1", previous, "retry")

    assert causality["triggered_by"] == "RETRY_BLOCKED"
    assert causality["triggered_by_record"].endswith(previous.name)
    assert causality["supersedes"] == ""


@pytest.mark.parametrize("verdict", ["PASS", "RETURN", "IN_PROGRESS"])
def test_retry_rejected_when_latest_is_not_blocked(feature, verdict):
    """6. BLOCKED 以外の状態では、再試行せず安全に停止すること。"""
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0001_x_g1.md",
                 verdict=verdict, gate="G1", run_seq=1, return_to="CP1")

    with pytest.raises(SystemExit) as error:
        fr.resolve_retry_action(root, CONFIG, feature_dir)

    assert "BLOCKED" in str(error.value)


def test_retry_rejected_without_any_record(feature):
    root, feature_dir = feature

    with pytest.raises(SystemExit):
        fr.resolve_retry_action(root, CONFIG, feature_dir)


def test_retry_rejected_when_blocked_gate_is_invalid(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0001_x_g9.md",
                 verdict="BLOCKED", gate="G9", run_seq=1, blocked_reason="state_error")

    with pytest.raises(SystemExit):
        fr.resolve_retry_action(root, CONFIG, feature_dir)


def test_retry_does_not_run_ai_when_rejected(sandbox, monkeypatch):
    """6'. 誤操作時に AI を起動しないこと。"""
    root, config, ctx = sandbox
    write_record(root / ctx["feature_dir"] / "gates", "0001_x_cp1.md",
                 verdict="PASS", gate="CP1", run_seq=1)

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    with pytest.raises(SystemExit):
        fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False, retry_blocked=True)

    assert fake.calls == []


def test_retry_and_review_current_are_mutually_exclusive(sandbox):
    root, config, ctx = sandbox

    with pytest.raises(SystemExit):
        fr.cmd_run(root, config, ctx, {}, once=False, dry_run=False,
                   review_current="G2", retry_blocked=True)


def test_retry_continues_into_normal_auto_mode(sandbox, monkeypatch):
    """7. 再試行の後は、通常のオートモードへ戻ること。"""
    root, config, ctx = sandbox
    blocked_record(root, ctx["feature_dir"], stage="CP1")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False, retry_blocked=True)

    action = fr.resolve_action(root, config, ctx["feature_dir"])

    # CP1 は Human Gate。再試行が PASS しても、仕様承認までは製造へ進まない
    assert (action.kind, action.stage) == ("await_human", "CP1")


def test_retry_does_not_pass_blocked_reason_as_human_note(sandbox, monkeypatch):
    """blocked_reason を人間コメントとして Reviewer へ渡さないこと。"""
    root, config, ctx = sandbox
    blocked_record(root, ctx["feature_dir"], stage="CP1", reason="guard_violation")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"], "recorded_by": "reviewer",
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, once=True, dry_run=False, retry_blocked=True)

    assert fake.reviewer_calls()[0]["human_note"] == ""


def test_retry_dry_run_shows_worker_without_executing(sandbox, monkeypatch):
    root, config, ctx = sandbox
    blocked_record(root, ctx["feature_dir"], stage="CP1")

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, once=True, dry_run=True, retry_blocked=True)

    assert code == 0
    assert fake.calls == []
    assert len(fr.list_records(root, ctx["feature_dir"])) == 1


def test_worker_receives_cheap_model_at_cp3(sandbox, monkeypatch):
    """CP3 の Worker に build ロール（既定 cheap）が割り当たること。"""
    root, config, ctx = sandbox
    gates = root / ctx["feature_dir"] / "gates"

    approve_spec(root, config, ctx)
    write_record(gates, "0002_x_g2.md", verdict="PASS", gate="G2", run_seq=2)

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
    "key", ["approval_heading_g1", "approval_heading_cp3", "human_note_heading"]
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


def test_current_workflow_docs_do_not_reference_removed_g0_stage():
    """新境界の正本文書・プロンプトに旧G0 stageを残さないこと。"""
    targets = [
        REPO_ROOT / "prompts/run_stage.md",
        REPO_ROOT / "prompts/review_stage.md",
        REPO_ROOT / "docs/rules/project/70_feature_loop.md",
        REPO_ROOT / "docs/templates/gate_record_template.md",
        REPO_ROOT / "tools/README.md",
    ]

    for target in targets:
        text = target.read_text(encoding="utf-8")
        assert "G0" not in text, target
        assert "_g0.md" not in text, target


def test_cp1_review_does_not_require_downstream_coverage():
    """CP1は設計前なのでreq_covered等を要求しないことを正本で固定する。"""
    text = (REPO_ROOT / "prompts/review_stage.md").read_text(encoding="utf-8")

    assert "`req_covered`: **空にする**" in text
    assert "**CP1は下流カバレッジ判定の対象外**" in text
    assert "G1は要求カバレッジ" in text


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

    fr.write_runner_record(root, ctx, "G1", "state_error", "状態を解決できません。", None)

    action = fr.resolve_action(root, CONFIG, feature_dir)

    assert action.kind == "stop"
    assert action.note == "state_error"


def test_invalid_verdict_becomes_error_action(feature):
    root, feature_dir = feature
    write_record(root / feature_dir / "gates", "0001_x_cp1.md", verdict="WEIRD", gate="CP1")

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

    broken = dict(CONFIG, human_gates="G1, G2, CP3")  # approval_heading_g2 がない

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


def test_status_reports_preflight_stop_when_approved_spec_changed(sandbox, capsys):
    """--status は製造開始条件NGなのに run と表示しないこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    spec = fr.spec_path(root, config, ctx)
    spec.write_text(spec.read_text(encoding="utf-8") + "変更\n", encoding="utf-8")

    code = fr.cmd_status(root, config, ctx)
    out = capsys.readouterr().out

    assert code == 0
    assert "製造開始条件: 満たしていない" in out
    assert "次の動作: Manufacturing Preflight で停止 (stage=G1)" in out
    assert "次の動作: run (stage=G1)" not in out


def test_status_reports_run_when_matching_spec_is_approved(sandbox, capsys):
    """承認済み baseline と一致する場合は従来どおり次 stage を表示すること。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)

    code = fr.cmd_status(root, config, ctx)
    out = capsys.readouterr().out

    assert code == 0
    assert "製造開始条件: 満たしている" in out
    assert "次の動作: run (stage=G1)" in out


# ---------------------------------------------------------------- 通過済み stage の成果物ハッシュ


def test_hash_paths_changes_with_content(sandbox):
    """内容が変われば artifacts_hash が変わること。"""
    root, config, ctx = sandbox
    patterns = fr.stage_artifacts(config, "G1", ctx)

    before = fr.hash_paths(root, patterns)
    (root / ctx["feature_dir"] / "21_design.md").write_text("変更後\n", encoding="utf-8")

    assert fr.hash_paths(root, patterns) != before


def test_hash_paths_is_stable_without_change(sandbox):
    root, config, ctx = sandbox
    patterns = fr.stage_artifacts(config, "G1", ctx)

    assert fr.hash_paths(root, patterns) == fr.hash_paths(root, patterns)


def test_hash_paths_detects_added_file_in_directory(sandbox):
    """ディレクトリ指定では、ファイルの追加も検出できること。"""
    root, _, _ = sandbox
    patterns = ["src/demo_app/features/"]

    (root / "src/demo_app/features").mkdir(parents=True)
    (root / "src/demo_app/features/a.py").write_text("a\n", encoding="utf-8")
    before = fr.hash_paths(root, patterns)

    (root / "src/demo_app/features/b.py").write_text("b\n", encoding="utf-8")

    assert fr.hash_paths(root, patterns) != before


def test_hash_paths_ignores_gitignored_files(sandbox):
    """__pycache__ のような無視対象を数えないこと。"""
    root, _, _ = sandbox
    (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")

    patterns = ["src/demo_app/features/"]
    (root / "src/demo_app/features").mkdir(parents=True)
    (root / "src/demo_app/features/a.py").write_text("a\n", encoding="utf-8")
    before = fr.hash_paths(root, patterns)

    cache = root / "src/demo_app/features/__pycache__"
    cache.mkdir()
    (cache / "a.pyc").write_bytes(b"\x00")

    assert fr.hash_paths(root, patterns) == before


def test_hash_paths_empty_without_patterns(sandbox):
    root, _, _ = sandbox
    assert fr.hash_paths(root, []) == ""


def pass_record(root, config, ctx, name, stage, seq):
    """artifacts_hash つきの PASS 記録（Reviewer が転記した想定）。"""
    return write_record(
        root / ctx["feature_dir"] / "gates", name,
        verdict="PASS", next_step="GO", gate=stage, run_seq=seq,
        recorded_by="reviewer",
        artifacts_hash=fr.current_artifacts_hash(root, config, ctx, stage),
    )


def test_stage_baseline_state_match_after_pass(sandbox):
    root, config, ctx = sandbox
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)

    assert fr.stage_baseline_state(root, config, ctx, "G1") == "match"


def test_stage_baseline_state_changed_after_edit(sandbox):
    root, config, ctx = sandbox
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)

    (root / ctx["feature_dir"] / "21_design.md").write_text("方式を変えた\n", encoding="utf-8")

    assert fr.stage_baseline_state(root, config, ctx, "G1") == "changed"


def test_stage_baseline_state_no_pass_before_gate(sandbox):
    root, config, ctx = sandbox
    assert fr.stage_baseline_state(root, config, ctx, "G1") == "no_pass"


def test_stage_baseline_state_unknown_for_record_without_hash(sandbox):
    """artifacts_hash を持たない過去の記録は判定不能として扱うこと（後方互換）。"""
    root, config, ctx = sandbox
    write_record(
        root / ctx["feature_dir"] / "gates", "0002_x_g1.md",
        verdict="PASS", gate="G1", run_seq=2,
    )

    assert fr.stage_baseline_state(root, config, ctx, "G1") == "unknown"


def test_stage_baseline_state_uses_latest_pass(sandbox):
    """同じ stage に複数の PASS がある場合、最新の PASS と比べること。"""
    root, config, ctx = sandbox
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)

    (root / ctx["feature_dir"] / "21_design.md").write_text("作り直した\n", encoding="utf-8")
    pass_record(root, config, ctx, "0005_x_g1.md", "G1", 5)

    assert fr.stage_baseline_state(root, config, ctx, "G1") == "match"


# ---------------------------------------------------------------- stale 判定


def test_stale_stages_empty_when_nothing_changed(sandbox):
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)

    assert fr.stale_stages(root, config, ctx) == []


def test_stale_stages_reports_g2_after_test_plan_edit(sandbox):
    """G2 の試験観点を変えたら G2 が stale になること。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text(
        "# 23_test_plan.md\n観点を1つ足した\n", encoding="utf-8",
    )

    assert fr.stale_stages(root, config, ctx) == ["G2"]


def test_stale_stages_reports_g1_after_design_edit(sandbox):
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)

    (root / ctx["feature_dir"] / "22_flow.md").write_text("処理方式を変えた\n", encoding="utf-8")

    assert fr.stale_stages(root, config, ctx) == ["G1"]


def test_stale_stages_reports_spec_stage_after_spec_edit(sandbox):
    """承認後に仕様を変えたら CP1 が stale になること。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)

    (root / ctx["feature_dir"] / "20_spec.md").write_text("期待動作を変えた\n", encoding="utf-8")

    assert fr.stale_stages(root, config, ctx) == ["CP1"]


def test_stale_stages_ignores_spec_before_first_approval(sandbox):
    """まだ一度も承認していない feature を stale と誤判定しないこと。"""
    root, config, ctx = sandbox
    assert fr.stale_stages(root, config, ctx) == []


def test_stale_stages_lists_upstream_first(sandbox):
    """複数 stage が変わった場合、stages 順（上流が先）で返すこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)

    (root / ctx["feature_dir"] / "21_design.md").write_text("設計変更\n", encoding="utf-8")
    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("観点追加\n", encoding="utf-8")

    assert fr.stale_stages(root, config, ctx) == ["G1", "G2"]


def test_describe_stale_names_downstream_and_both_recoveries(sandbox):
    root, config, _ = sandbox
    lines = "\n".join(fr.describe_stale(config, ["G2"]))

    assert "G2" in lines
    assert "CP3" in lines
    assert "--review-current G2" in lines
    assert "--rework G2" in lines


def test_describe_stale_points_spec_stage_to_spec_review(sandbox):
    """仕様 stage の復旧は --spec-review と再承認であること。"""
    root, config, _ = sandbox
    lines = "\n".join(fr.describe_stale(config, ["CP1"]))

    assert "--spec-review" in lines
    assert "--review-current CP1" not in lines


# ---------------------------------------------------------------- 完成後の変更で停止する


def approved_cp3(root, config, ctx, seq=4, name="0004_x_cp3.md"):
    """人間が受け入れ済みの CP3 PASS（= 完成状態）。"""
    record = pass_record(root, config, ctx, name, "CP3", seq)
    record.write_text(
        record.read_text(encoding="utf-8") + approval("受け入れ判断", True),
        encoding="utf-8",
    )
    return record


def completed_feature(root, config, ctx):
    """CP1 承認 → G1/G2 PASS → CP3 受け入れ済み、の完成状態を作る。"""
    (root / "src/demo_app/features").mkdir(parents=True, exist_ok=True)
    (root / "src/demo_app/features/demo.py").write_text("x = 1\n", encoding="utf-8")

    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)
    approved_cp3(root, config, ctx)


def test_completed_feature_reports_done(sandbox, capsys, monkeypatch):
    """何も変えていなければ、従来どおり完了と報告すること。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False)

    assert code == 0
    assert "完了しました。" in capsys.readouterr().out
    assert fake.calls == []


def test_done_stops_when_implementation_changed(sandbox, capsys, monkeypatch):
    """完成後に実装コードを直したら、完了扱いにせず停止すること。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / "src/demo_app/features/demo.py").write_text("x = 2\n", encoding="utf-8")

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False)
    out = capsys.readouterr().out

    assert code == 1
    assert "完了しました。" not in out
    assert "CP3" in out
    assert fake.calls == []


def test_done_stops_when_test_plan_changed(sandbox, capsys, monkeypatch):
    """完成後に G2 の試験観点を足したら、G2 と下流 CP3 を提示して停止すること。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text(
        "# 23_test_plan.md\nTV-007 を追加\n", encoding="utf-8",
    )

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))
    code = fr.cmd_run(root, config, ctx, {}, False, False)
    out = capsys.readouterr().out

    assert code == 1
    assert "変更が検出された stage: G2" in out
    assert "再確認が必要な下流 stage: CP3" in out


def test_done_stops_when_design_changed(sandbox, capsys, monkeypatch):
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "21_design.md").write_text("方式変更\n", encoding="utf-8")

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))
    code = fr.cmd_run(root, config, ctx, {}, False, False)
    out = capsys.readouterr().out

    assert code == 1
    assert "変更が検出された stage: G1" in out
    assert "再確認が必要な下流 stage: G2, CP3" in out


def test_done_stops_when_spec_changed(sandbox, capsys, monkeypatch):
    """完成後に仕様を変えたら、AI製造へ進まず停止すること。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "20_spec.md").write_text("期待動作を変えた\n", encoding="utf-8")

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False)
    out = capsys.readouterr().out

    assert code == 1
    assert "変更が検出された stage: CP1" in out
    assert "--spec-review" in out
    assert fake.calls == []


def test_stale_stop_does_not_write_gate_record(sandbox, monkeypatch):
    """stale の検出そのものは判断ではないので、Gate記録を増やさないこと。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)
    before = len(fr.list_records(root, ctx["feature_dir"]))

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("追加\n", encoding="utf-8")

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))
    fr.cmd_run(root, config, ctx, {}, False, False)

    assert len(fr.list_records(root, ctx["feature_dir"])) == before


def test_stale_stop_preserves_existing_records(sandbox, monkeypatch):
    """既存 Gate記録を書き換えないこと。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    records = fr.list_records(root, ctx["feature_dir"])
    before = {p.name: p.read_bytes() for p in records}

    (root / ctx["feature_dir"] / "21_design.md").write_text("変更\n", encoding="utf-8")

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))
    fr.cmd_run(root, config, ctx, {}, False, False)

    assert {p.name: p.read_bytes() for p in fr.list_records(root, ctx["feature_dir"])} == before


def test_await_human_stops_when_upstream_changed(sandbox, capsys, monkeypatch):
    """CP3 承認待ちの状態でも、上流が変わっていれば承認へ進ませないこと。"""
    root, config, ctx = sandbox
    (root / "src/demo_app/features").mkdir(parents=True, exist_ok=True)
    (root / "src/demo_app/features/demo.py").write_text("x = 1\n", encoding="utf-8")

    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)
    pass_record(root, config, ctx, "0004_x_cp3.md", "CP3", 4)  # 未承認

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("観点追加\n", encoding="utf-8")

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))
    code = fr.cmd_run(root, config, ctx, {}, False, False)
    out = capsys.readouterr().out

    assert code == 1
    assert "変更が検出された stage: G2" in out
    assert "人間の判断が必要です" not in out


def test_done_unaffected_for_records_without_artifacts_hash(sandbox, capsys, monkeypatch):
    """artifacts_hash を持たない既存 feature は、従来どおり完了と報告すること。"""
    root, config, ctx = sandbox
    (root / "src/demo_app/features").mkdir(parents=True, exist_ok=True)
    (root / "src/demo_app/features/demo.py").write_text("x = 1\n", encoding="utf-8")

    approve_spec(root, config, ctx)
    gates = root / ctx["feature_dir"] / "gates"
    write_record(gates, "0002_x_g1.md", verdict="PASS", gate="G1", run_seq=2)
    write_record(gates, "0003_x_g2.md", verdict="PASS", gate="G2", run_seq=3)
    record = write_record(gates, "0004_x_cp3.md", verdict="PASS", gate="CP3", run_seq=4)
    record.write_text(
        record.read_text(encoding="utf-8") + approval("受け入れ判断", True),
        encoding="utf-8",
    )

    # 実装を変えても、比較材料がないので停止しない（後方互換）
    (root / "src/demo_app/features/demo.py").write_text("x = 2\n", encoding="utf-8")

    monkeypatch.setattr(fr, "run_ai", FakeAI(root, lambda info: {}))
    code = fr.cmd_run(root, config, ctx, {}, False, False)

    assert code == 0
    assert "完了しました。" in capsys.readouterr().out


# ---------------------------------------------------------------- Reviewer への artifacts_hash


def test_reviewer_receives_artifacts_hash(sandbox, monkeypatch):
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"],
        "verdict": "PASS", "next_step": "GO",
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, True, False)

    passed = fake.reviewer_calls()[0]["artifacts_hash"]
    assert passed == fr.current_artifacts_hash(root, config, ctx, "G1")
    assert passed


def test_artifacts_hash_reflects_state_after_worker(sandbox, monkeypatch):
    """Worker が成果物を書き換えた後の状態が渡されること。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)

    design = root / ctx["feature_dir"] / "21_design.md"
    before = fr.current_artifacts_hash(root, config, ctx, "G1")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"],
        "verdict": "PASS", "next_step": "GO",
    })

    def worker_writes(root_, argv):
        if fr.WORKER_PROMPT in argv[1]:
            design.write_text("Worker が書いた設計\n", encoding="utf-8")
        return fake(root_, argv)

    monkeypatch.setattr(fr, "run_ai", worker_writes)

    fr.cmd_run(root, config, ctx, {}, True, False)

    passed = fake.reviewer_calls()[0]["artifacts_hash"]
    assert passed != before
    assert passed == fr.current_artifacts_hash(root, config, ctx, "G1")


def test_spec_stage_has_no_artifacts_hash(sandbox):
    """CP1 は spec_hash 側で判定するため artifacts_hash を使わないこと。"""
    root, config, ctx = sandbox
    assert fr.current_artifacts_hash(root, config, ctx, "CP1") == ""


# ---------------------------------------------------------------- --rework


def rework_ai(root, verdicts=None):
    """stage ごとに verdict を返す FakeAI。既定は常に PASS。"""
    verdicts = verdicts or {}

    return FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"],
        "verdict": verdicts.get(info["stage"], "PASS"), "next_step": "GO",
        "artifacts_hash": info["artifacts_hash"],
        "triggered_by": info["triggered_by"],
        "supersedes": info["supersedes"],
    })


def test_rework_runs_worker_then_reviewer(sandbox, monkeypatch):
    """--rework は Worker から再実行すること（--review-current との違い）。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, True, False, rework="G2")

    assert fake.prompts_used()[:2] == [
        f"{fr.WORKER_PROMPT} を参照してください。",
        f"{fr.REVIEWER_PROMPT} を参照してください。",
    ]
    assert fake.worker_calls()[0]["stage"] == "G2"


def test_rework_records_causality_and_supersedes(sandbox, monkeypatch):
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, True, False, rework="G2")

    call = fake.reviewer_calls()[0]
    assert call["triggered_by"] == "REWORK"
    assert call["supersedes"].endswith("0003_x_g2.md")


def test_rework_preserves_previous_records(sandbox, monkeypatch):
    """過去の Gate記録を削除も上書きもしないこと。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    before = {p.name: p.read_bytes() for p in fr.list_records(root, ctx["feature_dir"])}

    monkeypatch.setattr(fr, "run_ai", rework_ai(root))
    fr.cmd_run(root, config, ctx, {}, True, False, rework="G2")

    after = {p.name: p.read_bytes() for p in fr.list_records(root, ctx["feature_dir"])}

    assert set(before) < set(after)
    assert all(after[name] == data for name, data in before.items())


def test_rework_continues_into_downstream_stages(sandbox, monkeypatch):
    """--rework G2 のあと、CP3 まで自動で進むこと。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, False, False, rework="G2")

    assert [c["stage"] for c in fake.worker_calls()] == ["G2", "CP3"]


def test_rework_rejects_unknown_stage(sandbox):
    root, config, ctx = sandbox

    with pytest.raises(SystemExit) as error:
        fr.cmd_run(root, config, ctx, {}, False, False, rework="G9")

    assert "stages にありません" in str(error.value)


@pytest.mark.parametrize("other", [
    {"review_current": "G2"},
    {"retry_blocked": True},
    {"spec_review": True},
])
def test_rework_is_exclusive_with_other_modes(sandbox, other):
    root, config, ctx = sandbox

    with pytest.raises(SystemExit) as error:
        fr.cmd_run(root, config, ctx, {}, False, False, rework="G2", **other)

    assert "同時に指定できません" in str(error.value)


def test_rework_blocked_by_manufacturing_preflight(sandbox, monkeypatch):
    """仕様が未承認なら、--rework でも製造は始まらないこと。"""
    root, config, ctx = sandbox

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False, rework="G1")

    assert code == 1
    assert fake.calls == []
    assert latest_front(root, ctx)["blocked_reason"] == "spec_not_approved"


def test_rework_spec_stage_still_requires_human_approval(sandbox, monkeypatch):
    """--rework CP1 でも、AIが人間承認を代行しないこと。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False, rework="CP1")

    assert code == 0
    # CP1 の新しい PASS 記録が承認待ちで止まり、G1 以降へ進まないこと
    assert [c["stage"] for c in fake.worker_calls()] == ["CP1"]
    assert not fr.is_approved(fr.latest_record(root, ctx["feature_dir"]), "仕様承認")


def test_rework_dry_run_does_not_execute(sandbox, monkeypatch):
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, True, rework="G2")

    assert code == 0
    assert fake.calls == []


def test_dry_run_does_not_write_blocked_record(sandbox, monkeypatch):
    """--dry-run は Gate記録を増やさないこと。"""
    root, config, ctx = sandbox
    before = len(fr.list_records(root, ctx["feature_dir"]))

    monkeypatch.setattr(fr, "run_ai", rework_ai(root))
    code = fr.cmd_run(root, config, ctx, {}, False, True, rework="G1")

    assert code == 1
    assert len(fr.list_records(root, ctx["feature_dir"])) == before


# ---------------------------------------------------------------- 既存操作との住み分け


def test_retry_blocked_still_rejects_completed_feature(sandbox):
    """完成済み feature の修正へ --retry-blocked を流用できないこと。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("観点追加\n", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        fr.cmd_run(root, config, ctx, {}, False, False, retry_blocked=True)

    assert "BLOCKED からの復旧専用です" in str(error.value)


def test_review_current_recovers_human_edit_without_worker(sandbox, monkeypatch):
    """人間が直した成果物は、Worker を起動せずに再判定できること。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("人間が追記\n", encoding="utf-8")

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False, review_current="G2")

    assert code == 0
    assert fake.worker_calls() == []
    assert fake.reviewer_calls()[0]["mode"] == "manual"


def test_review_current_clears_stale_and_lets_downstream_run(sandbox, monkeypatch):
    """--review-current で G2 を通し直すと、下流 CP3 が再実行できる状態になること。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("人間が追記\n", encoding="utf-8")

    monkeypatch.setattr(fr, "run_ai", rework_ai(root))
    fr.cmd_run(root, config, ctx, {}, False, False, review_current="G2")

    assert fr.stale_stages(root, config, ctx) == []
    assert fr.resolve_action(root, config, ctx["feature_dir"]).stage == "CP3"


# ---------------------------------------------------------------- --status の表示


def test_status_reports_changed_stage(sandbox, capsys):
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("観点追加\n", encoding="utf-8")

    fr.cmd_status(root, config, ctx)
    out = capsys.readouterr().out

    assert "stage 成果物の baseline:" in out
    assert "通過後に変更あり" in out
    assert "次の動作: done" not in out


def test_status_reports_match_when_unchanged(sandbox, capsys):
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    fr.cmd_status(root, config, ctx)
    out = capsys.readouterr().out

    assert "通過時と同じ" in out
    assert "通過後に変更あり" not in out
    assert "次の動作: done" in out


def test_status_reports_unknown_for_legacy_records(sandbox, capsys):
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    write_record(
        root / ctx["feature_dir"] / "gates", "0002_x_g1.md",
        verdict="PASS", gate="G1", run_seq=2,
    )

    fr.cmd_status(root, config, ctx)

    assert "判定不能" in capsys.readouterr().out


# ---------------------------------------------------------------- 設定の整合


def test_config_artifacts_stay_within_worker_scope():
    """stage_*_artifacts は、その stage の Worker が変更できる範囲に収まること。"""
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo",
           "feature_dir": "docs/demo_app/features/demo"}

    for stage in fr.split_list(config["stages"]):
        allowed = fr.expand(config.get(f"stage_{stage.lower()}_worker", ""), ctx)

        for path in fr.stage_artifacts(config, stage, ctx):
            assert fr.is_allowed(path, allowed), f"{stage}: {path} が Worker の変更範囲外"


def test_config_artifacts_exclude_working_notes():
    """作業メモとレビュー結果を baseline に含めないこと。"""
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo",
           "feature_dir": "docs/demo_app/features/demo"}

    for stage in fr.split_list(config["stages"]):
        joined = " ".join(fr.stage_artifacts(config, stage, ctx))
        assert "tasks.md" not in joined
        assert "25_review_result.md" not in joined


def test_manufacturing_stages_have_artifacts_configured():
    """製造 stage には必ず artifacts 設定があること。"""
    config = fr.read_config(REPO_ROOT)
    ctx = {"app": "demo_app", "feature": "demo",
           "feature_dir": "docs/demo_app/features/demo"}

    for stage in fr.split_list(config["stages"]):
        if fr.is_manufacturing_stage(config, stage):
            assert fr.stage_artifacts(config, stage, ctx), stage


def test_rule_document_documents_rework():
    text = (REPO_ROOT / fr.CONFIG_DOC).read_text(encoding="utf-8")

    assert "--rework" in text
    assert "REWORK" in text
    assert "artifacts_hash" in text


def test_gate_record_template_has_artifacts_hash():
    text = (REPO_ROOT / "docs/templates/gate_record_template.md").read_text(encoding="utf-8")

    assert "artifacts_hash:" in text
    assert "REWORK" in text


# ---------------------------------------------------------------- 上流 stale での stage 実行


def test_run_stops_before_building_on_stale_upstream(sandbox, capsys, monkeypatch):
    """G2 が変更されていたら、CP3 の Worker を起動しないこと。

    実AI検証で見つかった穴。done / await_human だけを守っても、
    「G2 PASS のあと G2 を直して、次は CP3」という途中状態を守れない。
    """
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)

    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("観点追加\n", encoding="utf-8")

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False)
    out = capsys.readouterr().out

    assert code == 1
    assert "変更が検出された stage: G2" in out
    assert fake.calls == []


def test_run_stops_before_g2_when_design_is_stale(sandbox, capsys, monkeypatch):
    """G1 が変更されていたら、G2 の Worker も起動しないこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)

    (root / ctx["feature_dir"] / "21_design.md").write_text("方式変更\n", encoding="utf-8")

    fake = FakeAI(root, lambda info: {})
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, False, False)

    assert code == 1
    assert "変更が検出された stage: G1" in capsys.readouterr().out
    assert fake.calls == []


def test_run_ignores_own_stage_when_rerunning_it(sandbox, monkeypatch):
    """自分自身の stage の変更では止めないこと（作り直す対象なので）。

    RETURN(G1) の直後に、人間が 21_design.md を触っていても G1 は動かせる。
    """
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    write_record(
        root / ctx["feature_dir"] / "gates", "0003_x_g2.md",
        verdict="RETURN", gate="G2", run_seq=3, return_to="G1",
    )

    (root / ctx["feature_dir"] / "21_design.md").write_text("人間が直した\n", encoding="utf-8")

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"],
        "verdict": "PASS", "next_step": "GO",
        "artifacts_hash": info["artifacts_hash"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, True, False)

    assert [c["stage"] for c in fake.worker_calls()] == ["G1"]


def test_normal_progression_is_not_blocked_by_stale_check(sandbox, monkeypatch):
    """通常の進行（何も変更していない）を止めないこと。"""
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)

    fake = FakeAI(root, lambda info: {
        "gate": info["stage"], "run_seq": info["run_seq"],
        "verdict": "PASS", "next_step": "GO",
        "artifacts_hash": info["artifacts_hash"],
    })
    monkeypatch.setattr(fr, "run_ai", fake)

    fr.cmd_run(root, config, ctx, {}, True, False)

    assert [c["stage"] for c in fake.worker_calls()] == ["G2"]


def test_review_current_works_even_when_upstream_is_stale(sandbox, monkeypatch):
    """明示操作は、変更を承知のうえの指示なので止めないこと。"""
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "21_design.md").write_text("設計変更\n", encoding="utf-8")

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, True, False, review_current="G1")

    assert code == 0
    assert fake.reviewer_calls()[0]["stage"] == "G1"


def test_rework_works_even_when_upstream_is_stale(sandbox, monkeypatch):
    root, config, ctx = sandbox
    completed_feature(root, config, ctx)

    (root / ctx["feature_dir"] / "21_design.md").write_text("設計変更\n", encoding="utf-8")

    fake = rework_ai(root)
    monkeypatch.setattr(fr, "run_ai", fake)

    code = fr.cmd_run(root, config, ctx, {}, True, False, rework="G1")

    assert code == 0
    assert fake.worker_calls()[0]["stage"] == "G1"


def test_stale_stages_before_filters_to_upstream(sandbox):
    root, config, ctx = sandbox
    approve_spec(root, config, ctx)
    pass_record(root, config, ctx, "0002_x_g1.md", "G1", 2)
    pass_record(root, config, ctx, "0003_x_g2.md", "G2", 3)

    (root / ctx["feature_dir"] / "21_design.md").write_text("設計変更\n", encoding="utf-8")
    (root / ctx["feature_dir"] / "23_test_plan.md").write_text("観点追加\n", encoding="utf-8")

    assert fr.stale_stages(root, config, ctx) == ["G1", "G2"]
    assert fr.stale_stages(root, config, ctx, before="G2") == ["G1"]
    assert fr.stale_stages(root, config, ctx, before="G1") == []
    assert fr.stale_stages(root, config, ctx, before="CP1") == []

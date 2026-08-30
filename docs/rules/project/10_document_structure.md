# project: 文書構造（どこに何を置くか）

## このファイルの目的

このプロジェクトの成果物が、どの分類に属し、どこに置かれるかを定めます。

## このファイルを読む作業

- 文書を作成・更新する作業全般
- レビュー作業
- バグ対応
- 補助コンテキストを確認する作業

## このファイルに含めないもの

- **テンプレート対応表、文書種別ごとの見出し運用** → `15_document_templates.md`
- **いつ作成するか、どの順番で進めるか** → `20_workflow.md`
- レビュー結果の評価値 → `25_review_policy.md`
- 実装言語、実装規約 → `30_development_rules.md`
- テストの実行方法 → `40_testing_rules.md`
- AIの更新権限、保護対象 → `50_ai_permissions.md`
- 分類の定義そのもの → `docs/rules/core/40_official_docs_and_context.md`

---

## 成果物の分類

分類の定義は `docs/rules/core/40_official_docs_and_context.md` にあります。ここでは、このプロジェクトでの割り当てを示します。

### 正本（現在の仕様・設計・運用を定義する）

| 成果物 | 配置 |
|---|---|
| コマンド/アプリ全体の概要 | `docs/<command_or_app_name>/10_overview.md` |
| feature 仕様 | `docs/<command_or_app_name>/features/<feature_name>/20_spec.md` |
| 関数設計 | 同上 `/21_design.md` |
| 関数呼び出しフロー | 同上 `/22_flow.md` |
| feature 単体テスト計画 | 同上 `/23_test_plan.md` |
| 結合試験計画 | `docs/<command_or_app_name>/11_integration_test_plan.md` |
| 共通設計（目次・ファイル・データ・DB） | `docs/<command_or_app_name>/common_design/30_common_design_index.md`、`31_file_design.md`、`32_data_design.md`、`33_db_design.md` |

実装（`src/`）とテストコード（`tests/`）は、上記の正本の**下流**です。正本そのものではありませんが、変更時は正本との整合確認の対象です。

ただし、ここでいう整合確認は、**正本が定義している意味と矛盾していないか**の確認です。正本が意味を定義していない実装詳細（`docs/rules/core/40_official_docs_and_context.md`）が実装側にだけ存在することは、不整合として扱いません。

### 正式な管理記録（正式な工程の産物。仕様そのものは定義しない）

| 成果物 | 配置 |
|---|---|
| feature 単体レビュー観点・実装着手承認欄 | `.../features/<feature_name>/24_review_checklist.md` |
| feature 単体レビュー結果 | 同上 `/25_review_result.md` |
| **Gate記録（オートモード）** | 同上 `/gates/<連番4桁>_<タイムスタンプ>_<stage小文字>.md` |
| command/app 全体レビュー結果 | `docs/<command_or_app_name>/12_command_review_result.md` |
| バグ報告書 | `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md` |
| バグ調査書 | 同上 `/20_bug_investigation.md` |
| バグ修正計画書（人間承認欄を含む） | 同上 `/30_bug_fix_plan.md` |

これらは重要な証跡です。承認欄や判定を持つものもあります。
ただし、**仕様の根拠としては正本を参照します。** レビュー結果やバグ調査書の記述を、仕様の定義として扱わないでください。

### 提案・補助記録（確定仕様ではない）

| 成果物 | 配置 | 備考 |
|---|---|---|
| 共通化提案 | `docs/common/` 配下（作成する場合は `30_common_proposal.md`） | 現在は未作成 |
| 補助コンテキスト（会議メモ、過去判断、未決事項、却下案） | `docs/context/` 配下 | 詳細は `docs/context/README.md` |
| 旧AI作業ログ | `docs/context/ai_work_logs/` 配下 | **旧方式として凍結。新規作成しない**（`15_document_templates.md`）。既存記録は保持する |
| 現在地メモ | `docs/<command_or_app_name>/tasks.md`、`.../features/<feature_name>/tasks.md` | 位置づけは `docs/rules/core/50_records_and_reporting.md` |
| 作業メモ | `docs/context/work_notes/` 配下 | 作業の経緯・判断・手戻り・現在地を残す記録。保存方法の詳細な正本は `60_work_notes.md` |

**共通化提案は、採用されるまでは正本ではありません。**
採用された内容を正式資料へ反映する場合は、別の正式な変更作業として扱います（`docs/rules/core/40_official_docs_and_context.md`）。

### 3分類の対象外（人向け説明文書）

リポジトリ直下の `README.md` は、**現在は人向け説明文書**として扱います。上記3分類には入れません。

同様に、`docs/overview.md`、`docs/concept/` 配下、`docs/how_to_use_prompts.md`、`docs/tutorials/` 配下、`docs/prompt_design_notes.md` も人向け説明文書です。

将来、プロジェクトがこれらを正式な運用手順の正本として指定した場合は、**project ルールの変更として正本の一覧へ追加**できます。AIが独断で追加・除外しません。

### 一覧にない成果物

**一覧にない成果物を、AIが独断で「正本ではない」と判断してはなりません。**
判断できない場合は、確定させず人間確認事項として報告してください。

---

## ディレクトリ構成

docs、src、tests は `<command_or_app_name>` 単位で対応させます。

```text
docs/
  <command_or_app_name>/
    10_overview.md
    tasks.md
    11_integration_test_plan.md
    12_command_review_result.md
    common_design/
      30_common_design_index.md
      31_file_design.md
      32_data_design.md
      33_db_design.md
    features/
      <feature_name>/
        tasks.md
        20_spec.md
        21_design.md
        22_flow.md
        23_test_plan.md
        24_review_checklist.md
        25_review_result.md
        gates/
          0001_20260822T161400_cp1.md
          0002_20260822T163000_g1.md
    bugs/
      <bug_id>/
        10_bug_report.md
        20_bug_investigation.md
        30_bug_fix_plan.md

src/
  common/
    __init__.py
  <command_or_app_name>/
    __init__.py
    entrypoint.py
    features/
      __init__.py
      <feature_name>.py

tests/
  <command_or_app_name>/
    test_entrypoint_<short_name>.py
    test_integration_<short_name>.py
    features/
      test_<feature_name>.py
  tools/
    test_feature_runner.py
```

`tests/tools/` は、`tools/` 配下の補助ツールに対するテストです。command/app の feature テストとは別枠として扱います。

その他の置き場:

- `docs/common/`：共通化提案
- `docs/context/`：補助コンテキスト（`ai_work_logs/`、`work_notes/` を含む）
- `docs/templates/`：ひな形
- `prompts/`：汎用プロンプト

---

## 命名規約

- `<short_name>` は、単一 feature の command/app では feature 名を使います。複数 feature を束ねる command/app では、command/app を短く表す名前を使います。
- feature 名は機能単位の名前にします。関数名や実装上の処理名だけを理由に feature フォルダを分けません。
- 処理順・呼び出し順・パイプライン順が重要な場合は、feature フォルダ名に `010_`、`020_`、`030_` のような番号プレフィックスを付けてかまいません。ただし、Python の実装ファイル名やモジュール名まで番号付きにしません。
- 番号付き feature フォルダを使う場合も、フォルダ内のドキュメント番号体系（`20_spec.md`、`21_design.md` など）は変えません。
- `bug_id` は `bug_001` のような形式を基本とし、同一 command/app 内で重複しない名前にします。

---

## 変更する場合の注意

- ディレクトリ構成を変える場合、`docs/rules/core/10_workflow.md` の「仕様・実装・テストの対応関係を追える構成にする」を満たしているか確認してください。
- 成果物を追加する場合、**上記3分類のどれに属するかを必ず記載してください。** 分類が未記載の成果物は、AIが扱いを判断できません。
- 成果物を追加した場合は、`15_document_templates.md` のテンプレート対応も併せて確認してください。
- 人向け説明文書を正本へ昇格させる場合、AIが独断で行わず、project ルールの変更として扱ってください。

---

## 関連するルール

- 成果物の分類の定義 → `docs/rules/core/40_official_docs_and_context.md`
- どのひな形を使うか、見出しの扱い → `15_document_templates.md`
- いつ作成するか → `20_workflow.md`
- レビュー結果の評価値 → `25_review_policy.md`
- 誰が更新してよいか → `50_ai_permissions.md`
- 作業メモの保存方法・運用の具体値 → `60_work_notes.md`
- Gate記録の命名・front matter・immutable の扱い → `70_feature_loop.md`

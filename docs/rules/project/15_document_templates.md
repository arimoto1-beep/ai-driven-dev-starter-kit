# project: テンプレートの利用

## このファイルの目的

どの成果物にどのひな形を使うかと、文書種別ごとの見出し運用を定めます。

## このファイルを読む作業

- 文書を作成・更新する作業全般
- テンプレートを変更する作業
- テンプレートとプロンプトの整合を確認する作業

## このファイルに含めないもの

- ディレクトリ構成、成果物の配置と命名 → `10_document_structure.md`
- 工程の順番、いつ作成するか → `20_workflow.md`
- レビュー結果の評価値 → `25_review_policy.md`
- AIの更新権限、保護対象 → `50_ai_permissions.md`
- テンプレート運用の上位原則（見出しを勝手に変えない、空ファイルを作らない） → `docs/rules/core/40_official_docs_and_context.md`
- 各テンプレート本文の複製（本文は `docs/templates/` にあります）

---

## 現行スターターキットの初期値

### テンプレート対応表

| 作成する成果物 | ひな形 | 作成に使うプロンプト |
|---|---|---|
| `10_overview.md` | `docs/templates/10_overview_template.md` | `prompts/create_overview.md` |
| `20_spec.md` | `docs/templates/20_spec_template.md` | `prompts/create_feature_spec.md` |
| `21_design.md` | `docs/templates/21_design_template.md` | `prompts/create_function_design.md` |
| `22_flow.md` | `docs/templates/22_flow_template.md` | `prompts/create_function_call_flow.md` |
| `23_test_plan.md` | `docs/templates/23_test_plan_template.md` | `prompts/create_test_design.md` |
| `11_integration_test_plan.md` | `docs/templates/11_integration_test_plan_template.md` | `prompts/create_integration_test_plan.md` |
| `common_design/30_common_design_index.md` | `docs/templates/30_common_design_index_template.md` | `prompts/create_common_design_index.md` |
| `common_design/31_file_design.md` | `docs/templates/31_file_design_template.md` | `prompts/create_file_design.md` |
| `common_design/32_data_design.md` | `docs/templates/32_data_design_template.md` | `prompts/create_data_design.md` |
| `common_design/33_db_design.md` | `docs/templates/33_db_design_template.md` | `prompts/create_db_design.md` |
| `24_review_checklist.md` | `docs/templates/24_review_checklist_template.md` | `prompts/create_review_checklist.md` |
| `25_review_result.md` | `docs/templates/25_review_result_template.md` | `prompts/review_feature.md`（オートモード CP3 では `prompts/review_stage.md`） |
| `gates/<連番>_<日時>_<stage>.md` | `docs/templates/gate_record_template.md` | `prompts/review_stage.md` |
| `12_command_review_result.md` | `docs/templates/12_command_review_result_template.md` | `prompts/review_command.md` |
| `bugs/<bug_id>/10_bug_report.md` | `docs/templates/10_bug_report_template.md` | `prompts/create_bug_report.md` |
| `bugs/<bug_id>/20_bug_investigation.md` | `docs/templates/20_bug_investigation_template.md` | `prompts/investigate_bug.md` |
| `bugs/<bug_id>/30_bug_fix_plan.md` | `docs/templates/30_bug_fix_plan_template.md` | `prompts/create_bug_fix_plan.md` |
| `tasks.md` | `docs/templates/tasks_template.md` | 専用プロンプトなし |
| `30_common_proposal.md` | `docs/templates/30_common_proposal_template.md` | 専用プロンプトなし |
| `docs/context/` 配下のメモ | `docs/templates/context_note_template.md` | なし（人間が作成） |
| `docs/context/ai_work_logs/<date>_<task_id>_<summary>.md` | `docs/templates/ai_work_log_template.md` | **旧方式・新規作成しない**（下記参照） |
| `docs/context/work_notes/<work_folder>/README.md` | `docs/templates/work_note_readme_template.md` | `prompts/prepare_work_note.md` |

### 旧AI作業ログ（凍結）

**旧AI作業ログは旧方式として凍結しています。新しいAI作業ログは原則として作成しません。**

- 既存の記録（`docs/context/ai_work_logs/` 配下）と `docs/templates/ai_work_log_template.md` は、**当時の試行と経緯を確認するために保持します。削除しません。**
- 既存の記録の本文を、現在の考え方に合わせて書き直しません。
- **新しい作業知識の記録は、作業メモ（`docs/context/work_notes/`）で扱います。** 作業メモは導入済みです。保存方法・作成条件の正本は `docs/rules/project/60_work_notes.md`、新規作成・更新は `prompts/prepare_work_note.md` を使います。

### テンプレートがない成果物の扱い

- 上表にない成果物を作る必要が生じた場合、**AIが新しいテンプレートやひな形を勝手に作りません。**
- 既存のひな形を無理に流用せず、必要なひな形の追加候補として作業報告に記載し、人間判断へ回します。
- ひな形がないことは、その成果物が正本でないことを意味しません（`docs/rules/core/40_official_docs_and_context.md`）。

### 変更してはいけない対象（分類によらず共通）

- **テンプレートファイルそのもの**（`docs/templates/` 配下）は保護対象です。AIは人間の明示指示なしに変更しません（`50_ai_permissions.md`）。
- **テンプレートとして定義された標準構成**（見出しの追加・削除・順序変更・名称変更）を、AIが勝手に変更しません。

### 個別成果物での見出し運用

上の「変更してはいけない対象」とは別に、**作成する個別成果物の中で見出しをどう扱うか**を、分類ごとに定めます。
分類の定義と上位原則は `docs/rules/core/40_official_docs_and_context.md` にあります。

| 分類 | 対象（例） | 個別成果物での見出しの扱い |
|---|---|---|
| **正本** | `10_overview.md`、`20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md`、`11_integration_test_plan.md`、`common_design/` 配下 | **標準構成の見出しをすべて維持する。** 情報がない場合も削除せず、`未定`、`該当なし`、`確認中`、`人間判断待ち`、`今回は対象外` のように状態を記載する |
| **正式な管理記録** | `24_review_checklist.md`、`25_review_result.md`、`12_command_review_result.md`、`gates/` 配下、`bugs/<bug_id>/` 配下 | **標準構成の見出しをすべて維持する。** 証跡の欠落を防ぐため、正本と同じ扱いとする |
| **提案・補助記録** | `tasks.md`、`30_common_proposal.md`、`docs/context/` 配下 | **該当しない見出しを、その成果物の中で省略してよい。** 全項目を「該当なし」で埋める運用にはしない |

**提案・補助記録での見出しの省略は、テンプレート定義の変更には当たりません。** テンプレートファイルにも標準構成にも手を加えないためです。
省略してよいのは提案・補助記録だけです。正本と正式な管理記録では省略できません。

**例外：作業メモの `README.md`（`docs/context/work_notes/<work_folder>/README.md`）は、分類上は提案・補助記録ですが、必須見出しを省略しません。** README は入口・現在地・索引としての役割を持つため、`docs/rules/project/60_work_notes.md` が定める必須項目をすべて記載します（該当がない場合も「なし」と記載する）。任意項目は該当しない場合に省略できます。付随ファイルには、この例外は適用されません。付随ファイルには固定テンプレートを設けず、見出し構成も固定しません。

### 形式的な空ファイルを作らない

- まだ必要のない成果物を、見出しだけの状態で先に作成しません。
- 具体的には、レビューをまだ行っていない段階で `25_review_result.md` や `12_command_review_result.md` を作らず、作業状態を記録する必要がない段階で `tasks.md` を作りません。
- `common_design/` は、複数 feature にまたがる共通設計が必要になった場合に追加します。すべての command/app で必須ではありません。

---

## テンプレートを変更する場合の注意

テンプレートの見出しを変更すると、**そのテンプレートを出力先とするプロンプトと不整合になります。**

1. 上表の「作成に使うプロンプト」列で、影響するプロンプトを特定します。
2. プロンプトが要求している項目が、テンプレートの見出しとして存在するかを確認します。
3. テンプレートにあってプロンプトが触れていない見出しがないかを確認します。
4. 判定値を含むテンプレート（`25_review_result_template.md`、`12_command_review_result_template.md`）を変更する場合は、`25_review_policy.md` の「ラベルを変更する場合」に従ってください。集計ツールにも影響します。

### 不一致のレビュー方法

テンプレートとプロンプトの不一致は、`prompts/review_prompt_integrity.md` で確認します。

このプロンプトは、キット自体の整合性をレビューするためのものです。開発対象機能のレビューではありません。
「プロンプトとテンプレートの不一致」「出力テンプレートに存在しない項目をプロンプトが要求している箇所」「プロンプトが要求しているのにテンプレート側に欄がない箇所」を検出します。

テンプレートを変更したら、このプロンプトで整合を確認してください。

---

## 関連するルール

- テンプレート運用の上位原則、成果物の分類の定義 → `docs/rules/core/40_official_docs_and_context.md`
- 成果物の分類の割り当てと配置 → `10_document_structure.md`
- レビュー結果の評価値と集計ツールへの依存 → `25_review_policy.md`
- テンプレートの保護（AIは明示指示なしに変更しない） → `50_ai_permissions.md`
- 作業メモREADMEの必須項目・付随ファイルの扱いの詳細 → `60_work_notes.md`

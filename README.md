# AI駆動開発スターターキット

このリポジトリは、AIコーディングエージェントを使って、AI駆動開発の流れを小さく体験するためのスターターキットです。

目的は、完成度の高いアプリを作ることではありません。
人間が理解できる仕様と設計を用意し、それをもとにAIと一緒に小さく開発する流れを体験します。

---

## AI駆動開発コンセプト

このリポジトリでは、AIに実装を丸投げするのではなく、人間が理解できる仕様・設計・テスト観点を先に整理することを重視しています。
AIには小さな機能単位で実装を依頼し、人間が段階的に確認します。

詳細は [docs/concept/ai_driven_development.md](docs/concept/ai_driven_development.md) を参照してください。

---

## このリポジトリで体験できること

- AIに作業してもらうための入口（`AGENTS.md`）と、責務別ルール（`docs/rules/`）の使い方
- コマンド/アプリ単位で docs、src、tests を対応させる方法
- 個別機能を `features/<feature_name>/` で管理する方法
- 仕様、設計、呼び出し定義、テスト計画、レビュー観点を先に整理する流れ
- `entrypoint.py` と `features/` の責務を分ける流れ
- feature 単体レビューと command/app 全体レビューを分ける流れ
- `10_overview.md` を起点に、コマンド/アプリ全体と feature 分割を整理する流れ
- 必要に応じて、entrypoint から feature を束ねる結合試験計画を作る流れ
- バグをいきなり修正せず、報告 → 調査 → 修正計画 → 承認 → 実装の順に進む流れ
- コードを見て思いついた変更案を、バグ・仕様変更・設計改善・リファクタリング・標準化・共通化候補に整理してから作業に入る流れ
- `24_review_checklist.md` の実装着手承認欄を人間が確認し、承認なしでは feature 実装に進まない流れ

---

## 前提

- Python を実行できること
- GitHub Copilot Agent Mode を使えること
- 実装コードでは Python 標準ライブラリのみを使うこと
- 単体テストには `pytest` を使うこと

テスト実行用の最小依存として、`requirements.txt` に `pytest` のみを記載しています。

```bash
python -m pip install -r requirements.txt
```

---

## リポジトリ構成

```text
ai-driven-dev-starter-kit/
├─ README.md
├─ AGENTS.md                            ← AIが最初に読む薄い入口
├─ CLAUDE.md                            ← Claude Code向け補助入口
├─ docs/
│  ├─ overview.md
│  ├─ how_to_use_prompts.md
│  ├─ prompt_design_notes.md
│  ├─ rules/                            ← ルール内容の正本（詳細は rules/README.md）
│  │  ├─ README.md                      ← ルール体系の索引
│  │  ├─ core/                          ← プロジェクトに依存しない安全境界・上位原則
│  │  └─ project/                       ← このキット固有の設定（利用者が編集するのはここ）
│  ├─ concept/
│  │  └─ ai_driven_development.md
│  ├─ context/                          ← 補助コンテキスト
│  │  ├─ README.md
│  │  ├─ ai_work_logs/                  ← 旧AI作業ログ（凍結・新規作成しない）
│  │  │  ├─ README.md
│  │  │  └─ <date>_<task_id>_<summary>.md
│  │  ├─ work_notes/                    ← 作業メモ（現行の記録方式）
│  │  │  ├─ README.md
│  │  │  └─ <YYYYMMDD_short_name>/
│  │  └─ rejected_verbose_option.md
│  ├─ common/
│  │  └─ README.md
│  ├─ templates/
│  │  ├─ 10_overview_template.md
│  │  ├─ 10_bug_report_template.md
│  │  ├─ tasks_template.md
│  │  ├─ 20_spec_template.md
│  │  ├─ 20_bug_investigation_template.md
│  │  ├─ 21_design_template.md
│  │  ├─ 22_flow_template.md
│  │  ├─ 23_test_plan_template.md
│  │  ├─ 24_review_checklist_template.md
│  │  ├─ 11_integration_test_plan_template.md
│  │  ├─ 12_command_review_result_template.md
│  │  ├─ 25_review_result_template.md
│  │  ├─ 30_common_proposal_template.md
│  │  ├─ 30_bug_fix_plan_template.md
│  │  ├─ 30_common_design_index_template.md
│  │  ├─ 31_file_design_template.md
│  │  ├─ 32_data_design_template.md
│  │  ├─ 33_db_design_template.md
│  │  ├─ context_note_template.md
│  │  ├─ ai_work_log_template.md
│  │  └─ work_note_readme_template.md
│  ├─ tutorials/
│  │  ├─ 010_simple_calculator.md
│  │  ├─ 020_create_new_sample_from_scratch.md
│  │  ├─ 030_update_existing_feature.md
│  │  └─ 040_bug_fix_flow.md
│  ├─ cli_hello_greeting/
│  │  ├─ 10_overview.md
│  │  ├─ tasks.md
│  │  ├─ 11_integration_test_plan.md
│  │  ├─ 12_command_review_result.md
│  │  └─ features/
│  │     └─ greeting/
│  │        ├─ tasks.md
│  │        ├─ 20_spec.md
│  │        ├─ 21_design.md
│  │        ├─ 22_flow.md
│  │        ├─ 23_test_plan.md
│  │        ├─ 24_review_checklist.md
│  │        └─ 25_review_result.md
│  ├─ cli_simple_calculator/
│  │  ├─ 10_overview.md
│  │  ├─ tasks.md
│  │  └─ features/
│  │     └─ calculator/
│  │        ├─ tasks.md
│  │        └─ 20_spec.md
│  └─ cli_text_counter/
│     ├─ 10_overview.md
│     ├─ tasks.md
│     ├─ 11_integration_test_plan.md
│     ├─ 12_command_review_result.md
│     ├─ features/
│     │  └─ text_counter/
│     │     ├─ tasks.md
│     │     ├─ 20_spec.md
│     │     ├─ 21_design.md
│     │     ├─ 22_flow.md
│     │     ├─ 23_test_plan.md
│     │     ├─ 24_review_checklist.md
│     │     └─ 25_review_result.md
│     └─ bugs/                          ← バグ修正フローで使う
│        └─ <bug_id>/
│           ├─ 10_bug_report.md
│           ├─ 20_bug_investigation.md
│           └─ 30_bug_fix_plan.md
├─ prompts/
│  ├─ create_overview.md
│  ├─ create_feature_spec.md
│  ├─ create_function_design.md
│  ├─ create_function_call_flow.md
│  ├─ create_test_design.md
│  ├─ create_review_checklist.md
│  ├─ create_integration_test_plan.md
│  ├─ create_common_design_index.md
│  ├─ create_file_design.md
│  ├─ create_data_design.md
│  ├─ create_db_design.md
│  ├─ implement_feature.md
│  ├─ implement_entrypoint.md
│  ├─ implement_integration_test.md
│  ├─ review_feature_source.md
│  ├─ review_feature.md
│  ├─ review_command.md
│  ├─ review_context.md
│  ├─ analyze_code_change_impact.md      ← コード起点の変更案の影響範囲を整理する
│  ├─ create_bug_report.md
│  ├─ investigate_bug.md
│  ├─ create_bug_fix_plan.md
│  ├─ implement_bug_fix.md
│  ├─ prepare_work_note.md              ← 作業メモ(経緯・判断・手戻りの記録)を構成する
│  └─ review_prompt_integrity.md       ← スターターキット自体のプロンプト完全性レビュー用
├─ src/
│  ├─ common/
│  │  └─ __init__.py
│  ├─ cli_hello_greeting/
│  │  ├─ __init__.py
│  │  ├─ entrypoint.py
│  │  └─ features/
│  │     ├─ __init__.py
│  │     └─ greeting.py
│  └─ cli_text_counter/
│     ├─ entrypoint.py
│     └─ features/
│        └─ text_counter.py
├─ tests/
│  ├─ cli_hello_greeting/
│  │  ├─ test_entrypoint_greeting.py
│  │  ├─ test_integration_greeting.py
│  │  └─ features/
│  │     └─ test_greeting.py
│  └─ cli_text_counter/
│     ├─ test_entrypoint_text_counter.py
│     ├─ test_integration_text_counter.py
│     └─ features/
│        └─ test_text_counter.py
├─ tools/                               ← 品質確認ツール(quality_report.py 等)
├─ quality/                             ← 品質確認ツールの出力先
├─ requirements.txt
└─ LICENSE
```

---

## ルールはどこにあるか

このキットのルールは、責務ごとに分けて管理しています。**ルール内容の正本は `docs/rules/` 配下です。**

| 対象 | 役割 |
|---|---|
| `AGENTS.md` | AIが最初に読む**薄い入口**。常に守る原則と、どのルールを読むかの導線だけを持ちます |
| `docs/rules/core/` | プロジェクトに依存しない安全境界と上位原則（工程・承認・変更範囲・正式資料・記録） |
| `docs/rules/project/` | このキット固有の設定（文書構造・工程・実装規約・テスト規約・AIの権限）。**利用者が編集するのはここだけです** |
| `prompts/*.md` | task 固有の作業手順。各プロンプトの `## 必須参照ルール` に、その作業で読むルールが列挙されています |

以下のセクションは、この構造を人間が理解するための概要です。**詳細・最新の定義は各正本を参照してください。**

ルール体系の索引 → **[docs/rules/README.md](docs/rules/README.md)**

---

## docs / src / tests の対応関係

コマンド/アプリ単位で、同じ名前のまとまりを作ります。

```text
docs/<command_or_app_name>/
src/<command_or_app_name>/
tests/<command_or_app_name>/
```

個別機能は、それぞれの `features/` 配下で管理します。

```text
docs/<command_or_app_name>/features/<feature_name>/
src/<command_or_app_name>/features/<feature_name>.py
tests/<command_or_app_name>/features/test_<feature_name>.py
```

処理順・呼び出し順・パイプライン順が重要な場合は、feature フォルダ名に番号プレフィックスを付けてもよいです。

```text
docs/<command_or_app_name>/features/
├─ 010_load_inputs/
├─ 020_normalize_data/
├─ 030_compare_items/
└─ 040_output_result/
```

番号プレフィックスは、人間とAIが処理順を共有しやすくするためのものです。
Python の実装ファイル名やモジュール名まで番号付きにする必要はありません。
番号付き feature フォルダを使う場合も、フォルダ内のドキュメント番号体系（`20_spec.md` など）は変わりません。

`tasks.md` は作業状態を引き継ぐための現在地メモです。
command/app 単位の `docs/<command_or_app_name>/tasks.md` には全体の作業状態を、feature 単位の `docs/<command_or_app_name>/features/<feature_name>/tasks.md` には個別機能の作業状態を短く記録します。
仕様、設計、テスト計画、レビュー結果の代わりにはしません。
新しく作成する場合は、`docs/templates/tasks_template.md` を参考にします。

---

## 10_overview.md の位置づけ

`docs/<command_or_app_name>/10_overview.md` は、コマンド/アプリ全体の設計入口です。

ここでは、コマンド/アプリの目的、Boundary、`entrypoint.py`、feature 分割方針、機能一覧を整理します。
新しい機能を追加する場合は、まず 10_overview.md でコマンド/アプリ全体の責務と feature 分割を確認し、そのうえで `features/<feature_name>/` 配下のドキュメントを作成します。

---

## entrypoint と features の責務

`entrypoint.py` はCLI入口として薄く保ちます。

- CLI引数を受け取る
- `features/` 配下の機能を呼び出す
- 結果を標準出力に出す
- 終了コードを返す

`features/` 配下には、機能固有のロジックを置きます。
標準出力やCLI引数解析は原則として持たせません。

実装時は、feature 本体と entrypoint を分けて扱います。
`prompts/implement_feature.md` は feature 本体と feature 単体テストを作成し、`prompts/implement_entrypoint.md` は `entrypoint.py` と `test_entrypoint_<short_name>.py` を作成します。
entrypoint 実装中に feature が呼び出しにくい場合も、勝手に feature 実装を変更せず、見直し候補として報告します。

entrypoint テストと結合試験の標準命名は以下です。

```text
tests/<command_or_app_name>/test_entrypoint_<short_name>.py
tests/<command_or_app_name>/test_integration_<short_name>.py
```

`<short_name>` は、単一 feature の command/app では feature 名を使います。
複数 feature を束ねる command/app では、command/app を短く表す名前を使います。

実装規約の詳細（言語、依存、命名、entrypoint と features の責務）→ `docs/rules/project/30_development_rules.md`

---

## 結合試験の位置づけ

このスターターキットにおける結合試験は、`entrypoint.py` から複数 feature を束ねて呼び出し、コマンド/アプリとして期待どおり動くことを確認するものです。

feature 単体の詳細ロジックは、各 feature の単体試験で確認します。
結合試験では、`entrypoint.py`、feature 呼び出し、入出力、終了コード、エラー時の扱いを確認します。

結合試験計画は、必要に応じて `docs/<command_or_app_name>/11_integration_test_plan.md` に作成します。
常に必須ではなく、entrypoint から feature を束ねて確認する必要がある場合に扱います。

試験の単位、検証コマンド、テストファイルの配置 → `docs/rules/project/40_testing_rules.md`

---

## 実装前承認ゲート

feature 実装に進む前に、`24_review_checklist.md` の末尾にある実装着手承認欄を人間が確認してチェックを入れてください。
承認欄に未チェック項目がある場合、`prompts/implement_feature.md` は STOP します。
これは、設計完了後にAIが勝手に実装へ進まないためのゲートです。

承認境界と停止判断（次工程移行判定を含む）の詳細 → `docs/rules/core/20_approval_and_review.md`
承認欄の場所と承認者 → `docs/rules/project/50_ai_permissions.md`

---

## コード起点の変更検討

コードを読んでいて変更を思いついた時点では、それがバグなのか、仕様変更なのか、設計改善・リファクタリング・類似機能間の整合性改善・標準化・共通化候補なのかが未確定な場合があります。仕様どおり正常に動いていても、内部構造を改善したい場合や、類似機能と実装方式をそろえたい場合があります。

分類が未確定なまま作業を始めず、まず `prompts/analyze_code_change_impact.md` で影響範囲を整理します。このプロンプトはファイルを変更せず、変更の分類・影響する資産・次に進むべきフローをチャットで報告します。

分析では、影響するファイルを列挙するだけでなく、変更内容を定義すべき最上流かつ役割の合う正式資料を「正本」として特定します。人間が正本と更新順を確認した後、上流から下流へ順番に反映します。上流資料を形式的にすべて変更するわけではなく、変更不要な上流資料は理由を示して更新しません。現在の構成に適切な正本がない場合は、AIが新しい資料を作らず人間判断に戻します。詳しい判断基準は `prompts/analyze_code_change_impact.md` と `docs/rules/core/10_workflow.md` を参照してください。

分析結果を人間が確認したうえで、バグ候補ならバグ修正フローへ、仕様変更なら仕様変更の流れへ進みます。共通化候補の場合も、AIが `src/common/` を勝手に変更することはありません。

実装済み feature に対する変更全般の進め方は `docs/tutorials/030_update_existing_feature.md` を参照してください。

---

## バグ修正フロー

このキットでは、バグを見つけてもすぐ修正せず、おおむね次のように段階を分けます。

1. **バグ報告書を作成する**（`prompts/create_bug_report.md`）
   - 現象、期待動作、再現手順を整理する。原因は断定しない。修正しない。
2. **バグを調査する**（`prompts/investigate_bug.md`）
   - 仕様・設計・実装・テストを読み、原因仮説を整理する。修正しない。
3. **修正計画書を作成する**（`prompts/create_bug_fix_plan.md`）
   - 修正対象、テスト方針、確認コマンドを明記する。修正しない。
4. **人間が修正計画書を承認する**
   - 承認欄にチェックを入れる。
5. **修正を実装する**（`prompts/implement_bug_fix.md`）
   - 承認済み計画の範囲だけを修正する。ついで修正はしない。

バグ管理ドキュメントは `docs/<command_or_app_name>/bugs/<bug_id>/` に配置します。
仕様・設計・テスト計画への反映が必要な場合は、修正実装とは別作業として扱います。

上記は流れをつかむための説明です。**正確な工程、承認条件、各 task の責務は `docs/rules/project/20_workflow.md` と対応する task プロンプトを参照してください。**

---

## レビューの位置づけ

レビューは段階的に扱います。

- feature ソースレビュー: `prompts/review_feature_source.md` を使い、実装直後にソースコードの問題をチャットで報告します。ファイルは変更しません。
- feature 単体レビュー: `prompts/review_feature.md` を使い、結果を `<対象機能フォルダ>/25_review_result.md` に記録します
- command/app 全体レビュー: `prompts/review_command.md` を使い、結果を `docs/<command_or_app_name>/12_command_review_result.md` に記録します

`review_feature_source.md` は implement_feature.md 直後の中間チェックです。修正は行わず、修正候補を報告するだけです。
`review_feature.md` は feature の仕様、設計、実装、単体テストに集中します。
entrypoint と結合試験まで含めた最終確認は `review_command.md` で扱います。

既存のレビュー結果がある場合でも、古い判定をそのまま採用せず、現在のファイル群を読み直して再レビューします。

`docs/context/`（補助コンテキスト）の横断探索は、通常レビューから分離して `prompts/review_context.md` が専任で扱います。通常レビューやバグ調査で context を読み込みすぎると、本来の確認が終わらなくなるためです。

`review_context.md` は候補を出すだけで、ファイルを変更しません。採用・却下・保留は人間が判断します。

各 task が context をどこまで読み、何を変更できるかは、対応する `prompts/*.md` を参照してください。

レビュー結果の評価値と記録先 → `docs/rules/project/25_review_policy.md`
レビューと修正の分離、次工程移行判定 → `docs/rules/core/20_approval_and_review.md`

---

## 共通設計書の位置づけ

DB設計、ファイル設計、共通データ設計など、複数 feature にまたがる設計は、feature 個別の設計書に分散させず、`docs/<command_or_app_name>/common_design/` 配下にまとめます。

feature 個別の `21_design.md` では、必要に応じて共通設計書を参照します。

共通設計書は、人間が直接作成しても構いません。AIに作成させる場合は、対応する `prompts/create_*_design.md` を使用します。

| 設計書 | ひな形 | 作成プロンプト | 内容 |
|---|---|---|---|
| `common_design/30_common_design_index.md` | `30_common_design_index_template.md` | `create_common_design_index.md` | 共通設計書の目次・feature 対応表 |
| `common_design/31_file_design.md` | `31_file_design_template.md` | `create_file_design.md` | 入出力・中間ファイル・ディレクトリ構成 |
| `common_design/32_data_design.md` | `32_data_design_template.md` | `create_data_design.md` | 共通データ項目・ID体系・ステータス |
| `common_design/33_db_design.md` | `33_db_design_template.md` | `create_db_design.md` | DB種別・テーブル・カラム・制約・トランザクション方針 |

**全成果物とひな形の対応関係の正本は `docs/rules/project/15_document_templates.md` です。**

`common_design/` は必要になった場合に追加する拡張です。すべてのコマンド/アプリで必須ではありません。

---

## common の扱い

`src/common/` は共通処理置き場です。

ただし、AIは人間の明示指示なしに `src/common/` を作成・更新しません。
共通化候補がある場合は、設計書、レビュー結果、作業報告に提案として記録します。
提案をまとめる場合は、`docs/templates/30_common_proposal_template.md` を使います。

保護対象とAIの更新権限の詳細 → `docs/rules/project/50_ai_permissions.md`

---

## prompts の使い方

`prompts/` 直下には、実プロジェクトでも使う汎用プロンプトだけを配置します。
チュートリアル専用プロンプトは置きません。

汎用プロンプトは直接書き換えず、チャットで以下を渡して使います。

- 参照するプロンプトのパス
- 対象機能フォルダ
- コマンド/アプリ名
- 対象機能名
- 実装ファイル
- テストファイル
- 補足条件

詳しくは `docs/how_to_use_prompts.md` を参照してください。

---

## はじめて使う場合

はじめて使う場合は、以下の順番で確認してください。

1. `README.md` で全体像を確認する
2. `docs/concept/ai_driven_development.md` でこのキットの考え方を確認する
3. `docs/how_to_use_prompts.md` で汎用プロンプトの使い方を確認する
4. `docs/tutorials/010_simple_calculator.md` で単一 feature の流れを体験する
5. `docs/tutorials/020_create_new_sample_from_scratch.md` で複数 feature を持つサンプルをゼロから作る
6. 必要に応じて `docs/overview.md` でドキュメント構成を確認する

まず雰囲気だけ掴みたい場合は、チュートリアル 010 の「設計 → 実装 → テスト」の流れ（関数設計から feature 実装・テスト実行まで）を進めれば、AI駆動開発の1周を体験できます。
entrypoint の分離、結合試験、3層レビュー、common_design は、実プロジェクトに適用するときの拡張です。
最初からすべてを完璧に進める必要はありません。

実際の作業では、`prompts/*.md` を直接編集せず、チャットで「参照するプロンプトのパス」と「対象機能情報」を渡して使います。

---

## チュートリアル

`docs/tutorials/` に、以下のチュートリアルを配置しています。

| ファイル | 目的 |
|---|---|
| `010_simple_calculator.md` | 既存の初期状態サンプル（cli_simple_calculator）を使って進める。単一 feature の設計・実装・テスト・レビューを体験する。 |
| `020_create_new_sample_from_scratch.md` | 新しいサンプルを1から作る。複数 feature に分ける 10_overview.md の作り方と、docs / features / tasks.md の初期構造を体験する。 |
| `030_update_existing_feature.md` | 実装済み feature に対して、仕様変更・軽微な機能追加・内部設計の改善・リファクタリング・類似機能間の整合性改善・レビュー指摘反映を安全に行う流れを確認する。コード起点の変更案は `analyze_code_change_impact.md` で分類・影響範囲を整理してから進める。バグ修正は 040 を参照。 |
| `040_bug_fix_flow.md` | バグ修正専用フロー。報告・調査・修正計画・人間承認・実装の順番を想定バグを使って確認する。 |

`cli_text_tools` はリポジトリに最初から配置されているサンプルではありません。020 チュートリアルの中で読者が作成する題材です。

いずれも `prompts/` 直下の汎用プロンプトを参照し、チャットで対象機能情報を渡して進めます。

---

## サンプル

このリポジトリには、用途の異なる3つのサンプルを配置しています。

### cli_hello_greeting（完成済みサンプル）

docs / features / tasks.md の完成形を確認するためのサンプルです。
仕様・設計・実装・テスト・レビューがすべて揃っています。

実行例:

```bash
python src/cli_hello_greeting/entrypoint.py --name Alice
```

期待する出力:

```text
Hello, Alice!
```

### cli_simple_calculator（チュートリアル用初期状態）

`docs/tutorials/010_simple_calculator.md` に従って、仕様・設計・実装・テスト・レビューを段階的に進めるためのサンプルです。
`10_overview.md` / `20_spec.md` / `tasks.md` が配置済みで、ここから作業を開始します。

### cli_text_counter（tasks.md 運用まで含めた完成済みサンプル）

初期ドキュメント配置から実装・テスト・レビューまで一通り進めた完成済みサンプルです。
tasks.md の運用を含む完成形を確認できます。

---

## テスト実行

```bash
python -m pytest
```

試験の単位や配置を含むテスト規約 → `docs/rules/project/40_testing_rules.md`

---

## 注意事項

- 仕様にない機能を勝手に追加しないでください
- 外部ライブラリは原則使わないでください
- CI/CD、デプロイ資産は追加しないでください
- 結合試験は、計画があり必要な場合だけ扱ってください
- feature 単体レビューと command/app 全体レビューを混ぜないでください
- `entrypoint.py` を厚くしないでください
- feature 固有ロジックを `entrypoint.py` に入れないでください
- `src/common/` に勝手に共通処理を追加しないでください
- 結合試験中にテストしにくい点があっても、勝手に実装コードを変更しないでください
- チュートリアル専用プロンプト置き場は作成しないでください

ここに挙げたのは代表例です。**AIが守るルールの正本は `docs/rules/` 配下です**（索引: [docs/rules/README.md](docs/rules/README.md)）。

---

## ライセンス

このプロジェクトは MIT License で公開しています。

著作権表示およびライセンス本文を含めることで、
商用・非商用を問わず、利用・改変・再配布できます。

詳細は [LICENSE](./LICENSE) を参照してください。

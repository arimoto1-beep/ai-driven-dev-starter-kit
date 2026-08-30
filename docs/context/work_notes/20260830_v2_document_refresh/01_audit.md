# 調査結果：現在仕様と食い違う記述の一覧

2026-08-30 に実施した調査の結果です。**この調査で確認した内容だけを記載しています。**
推測で問題を追加していません。

調査方法は、文字列検索だけでなく、正本（`70_feature_loop.md`）・実装（`tools/feature_runner.py`）・
テスト（`tests/tools/test_feature_runner.py`）・入口文書・rules・prompts・templates・tutorials・
サンプル docs を実際に読んだうえで、各記述が「履歴」か「現在仕様の説明」かを判定しています。

---

## 優先度：高

### H-1. `docs/overview.md` 「実装前承認ゲート」（116-121行付近）

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「feature 実装（`prompts/implement_feature.md`）に進む前に、`24_review_checklist.md` 末尾の実装着手承認欄を人間が確認してチェックを入れる。承認欄に未チェック項目がある場合、AIは実装を開始せず STOP する」 |
| 何が問題か | **無条件の規則として書かれている。** 現行では `24_review_checklist.md` の「実装開始条件」が `manual` のときだけ成立する。`auto` では**この欄は使用せず、未チェックのまま残るのが正常**（`70_feature_loop.md` の「実装開始条件」）。AIがこの節だけを読むと、オートモードの feature で誤って STOP する経路になる |
| あるべき説明 | 実装開始条件は2方式ある。`manual` はこの承認欄、`auto` は「CP1 の仕様承認（現在の `20_spec.md` と同一 baseline）AND 最新 G2 Gate記録の `verdict: PASS`」。正本は `70_feature_loop.md`「実装開始条件」 |
| 優先度 | 高 |

### H-2. `docs/templates/24_review_checklist_template.md`（90行付近）

| 項目 | 内容 |
|---|---|
| 現在の記述 | `| auto | **CP1 の下流進行承認 AND 最新 G2 Gate記録の verdict: PASS** |` |
| 何が問題か | ① **「下流進行承認」は現行に存在しない用語**（現行は「仕様承認」）。② **「現在の `20_spec.md` と同一 baseline」という必須条件が欠落**している。テンプレートなので、今後作られる全 feature の `24_review_checklist.md` へ伝播する |
| あるべき説明 | 「**CP1 の仕様承認（現在の `20_spec.md` と同一 baseline）AND 最新 G2 Gate記録の `verdict: PASS`**」。`20_workflow.md` と `50_ai_permissions.md` の表現に揃える |
| 優先度 | 高 |

### H-3. `README.md` 全体 — オートモードの記載がゼロ

| 項目 | 内容 |
|---|---|
| 現在の記述 | 全体がマニュアルモード前提。grep の結果、`README.md` / `AGENTS.md` / `CLAUDE.md` / `docs/README.md` / `docs/overview.md` / `docs/how_to_use_prompts.md` / `docs/concept/ai_driven_development.md` / `docs/tutorials/README.md` の**すべてでオートモード・`feature_runner`・Gate記録の言及が0件** |
| 何が問題か | 該当箇所は次のとおり。<br>・「このリポジトリで体験できること」：Worker/Reviewer の分離レビュー、Gate、仕様承認境界が挙がっていない<br>・「リポジトリ構成」ツリー：`tools/feature_runner.py` も `features/<name>/gates/` も無い<br>・「作業の全体像」表：`70_feature_loop.md` への導線が無い<br>・「はじめて使う場合」：5ステップすべてマニュアル前提で、最後に 010（マニュアル）へ誘導 |
| あるべき説明 | feature 新規開発の標準はオートモード。人間が用意するのは `20_spec.md`、承認するのは CP1 と CP3 の2点、間は AI が回す。マニュアルモードは工程を細かく刻みたい場合に使える |
| 優先度 | 高 |

### H-4. `README.md` 「想定する利用環境」（19行付近）

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「GitHub Copilot Agent Modeなど、リポジトリ内の文書を参照できるAIコーディングエージェント」 |
| 何が問題か | オートモードは `ai_command`（例：`claude,-p,{instruction},--model,{model}`）で**非対話の AI CLI をサブプロセス起動**する。IDE 内のエージェントモードだけでは runner は動かない |
| あるべき説明 | ①マニュアルモードは文書を読める任意の AI エージェント（Copilot Agent Mode など）で動く、②オートモードは追加で「`-p` 相当の非対話実行とモデル指定ができる AI CLI」が必要、と分けて書く |
| 優先度 | 高 |

### H-5. `docs/overview.md` — 構成説明がオートモードに追随していない

| 該当箇所 | 何が問題か |
|---|---|
| 「基本構成」ツリー | `features/<feature_name>/gates/` が無い。正本の `10_document_structure.md` には**ある** |
| 「各ファイルの役割」表 | Gate記録の行が無い |
| 「## prompts」節 | `review_feature_source.md`・`analyze_code_change_impact.md` 等は詳述されているのに、`run_stage.md` / `review_stage.md` の説明が無い |
| 「## 今回の対象範囲」 | 対象一覧が全部マニュアル工程。Spec Review、Gate判定、収束ループが無い |

あるべき説明：正本（`10_document_structure.md`、`70_feature_loop.md`）に合わせ、`gates/` と Gate記録、
オートモードの2プロンプトを構成説明へ追加する。**優先度 高**

---

## 優先度：中

### M-1. `docs/rules/project/10_document_structure.md`（115行付近）— 存在しない stage の例

| 項目 | 内容 |
|---|---|
| 現在の記述 | ディレクトリ構成例に `gates/0001_20260822T161400_g0.md` |
| 何が問題か | 現行の `stages = CP1, G1, G2, CP3` に `G0` は存在しない。**正本の中に実在しない stage の例がある** |
| あるべき説明 | `0001_..._cp1.md` / `0002_..._g1.md` のような、実在する stage の例にする |
| 優先度 | 中（正本内の誤例のため、中〜高で扱ってよい） |

### M-2. `docs/rules/project/20_workflow.md` — マニュアルを「標準工程」と呼んでいる

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「## 標準工程」（マニュアルモードの16工程）が先頭、「## オートモード」が後続の節。「**オートモードは、上記の標準工程を置き換えません。**」 |
| 何が問題か | **内容自体は正確**（承認を置く工程の表、実装開始条件の表とも現行仕様と一致）。問題は**位置づけと呼称**で、feature 新規開発の表玄関をオートモードにする方針と食い違って読める |
| あるべき説明 | 節の順序と「標準工程」という呼称を見直す。**内容の書き換えではなく、順序と表現の調整にとどめる** |
| 優先度 | 中 |

### M-3. `docs/tutorials/` 4本すべて — オートモードのチュートリアルが無い

| ファイル | 該当箇所 | 何が問題か |
|---|---|---|
| `010_simple_calculator.md` | 「## 5a. 実装着手承認欄を確認する（人間が行う）」（197行付近） | **新規 feature 開発における人間承認として、実装着手承認を教えている。** 現行の標準は CP1 仕様承認。Spec Review・CP1・Gate記録に一度も触れない。さらに 010 は関数設計から始まり、`20_spec.md` を作る工程自体が無い |
| `020_create_new_sample_from_scratch.md` | 導線図（336-337行付近）「【人間作業】24_review_checklist.md の実装着手承認欄を確認し、すべてチェックを入れる」 | 同上 |
| `030_update_existing_feature.md` | 243行、260行、516行 | 「ルートAでも実装着手承認欄の確認は通常どおり必要」が無条件表現。オートモードの feature ではこの欄を使わない |
| `tutorials/README.md` | 「初めて一連の流れを試す場合は 010」 | 新規利用者の最初の体験がマニュアルモードになる |

あるべき姿：オートモードのチュートリアル（`20_spec.md` を書く → `--spec-review` → CP1 承認 →
runner を回す → CP3 受け入れ）を新設し、入口をそちらにする。**既存4本は削除せず、
マニュアルモードで進める例として維持する。** 優先度 中（新規利用者の最初の体験なので中〜高）

### M-4. `prompts/analyze_code_change_impact.md`（609行付近）

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「実装とテストの変更作業（… **実装着手承認欄の確認は通常どおり必要です**）」 |
| 何が問題か | オートモードの feature では成立しない。M-3 の 030 と同じ無条件表現 |
| あるべき説明 | 実装開始条件の方式（`manual` / `auto`）に応じた条件付き表現にする |
| 優先度 | 中 |

### M-5. `docs/how_to_use_prompts.md` — オートモードへの導線が無い

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「## どこから始めるか」が 010 のみ。「## 汎用プロンプト一覧」に `run_stage.md` / `review_stage.md` が無い |
| 何が問題か | **AIも人間も入口として読む文書**なのに、runner 経由の使い方に到達できない |
| あるべき説明 | オートモードの使い方（runner が2プロンプトを起動する、単独手動実行もできる）を1節追加する |
| 優先度 | 中 |

### M-6. `docs/README.md` — 案内表とサンプル表

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「どこから読むか」表にオートモード／`tools/feature_runner.py` の行が無い。「コマンド／アプリの設計文書」表は3件 |
| 何が問題か | `docs/` には**6件のディレクトリがある**（M-7 参照）。案内と実態が一致していない |
| あるべき説明 | オートモードの行を追加し、サンプル表を実態に合わせる（M-7 の判断後） |
| 優先度 | 中 |

### M-7. 案内されていないサンプル3件

`docs/cli_text_masker/` / `docs/cli_mask_rework/` / `docs/cli_uppercase_text/` は、
**リポジトリ内のどこからも参照されていません**（`work_notes` を除く）。実AI検証の残骸です。

| ディレクトリ | 状態 |
|---|---|
| `cli_text_masker` | docs / src / tests あり。`gates/` あり。`24_review_checklist.md` は `方式: auto` |
| `cli_mask_rework` | docs / src / tests あり。`gates/` あり。`24_review_checklist.md` は `方式: auto` |
| `cli_uppercase_text` | **`20_spec.md` / `21_design.md` / `22_flow.md` / `gates/` / `tasks.md` のみ。`23_test_plan.md` 以降なし、src / tests もなし**。未完成のまま放置 |

何が問題か：AIがリポジトリを読むと「これも標準的な例だ」と解釈しかねません。特に
`docs/cli_uppercase_text/features/uppercase/tasks.md`（20行付近）は
**「G0 Gate のレビューを実施する」** と、存在しない stage を現在地メモに記録しています。

一方で `cli_text_masker` / `cli_mask_rework` は**オートモードの実例として価値がある**
（`gates/` に実際の Gate記録がある）ため、削除ではなく「オートモードのサンプル」として
正式に案内する選択肢もあります。**扱いは人間の判断事項です。** 優先度 中

### M-8. `AGENTS.md` の作業分類表

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「実装・変更」の起点に `core/10_workflow.md`、`core/30_change_safety.md`、`project/20_workflow.md`、`project/30_development_rules.md`、`project/40_testing_rules.md`、`project/50_ai_permissions.md` |
| 何が問題か | **`project/70_feature_loop.md` が無い。** task プロンプト指定時は `run_stage.md` / `review_stage.md` の `## 必須参照ルール` 経由で到達できるが、**プロンプト指定なしでオートモードの作業を頼まれたAIは正本に届かない** |
| あるべき説明 | 「実装・変更」の起点に `project/70_feature_loop.md` を追加する |
| 優先度 | 中 |

### M-9. `docs/concept/ai_driven_development.md`

| 項目 | 内容 |
|---|---|
| 現在の記述 | 「8. レビューを段階化する」等がマニュアル工程前提 |
| 何が問題か | Worker/Reviewer の分離（レビュー独立性 L1）、Gate、仕様承認境界という現在の中核概念が思想文書に反映されていない |
| あるべき説明 | 現在の考え方（AIレビューを別プロセスで独立させる、人間の判断点を2つに絞る）を反映する |
| 優先度 | 中（思想文書なので急がないが、コンセプトと実装の乖離ではある） |

---

## 優先度：低

### L-1. `quality/README.md`

Gate記録に触れていません。ただし `docs/rules/project/25_review_policy.md` が
「オートモードでも集計は変わらない」と明記済みで実害は小さいため、1行の補足で足ります。優先度 低

### L-2. `docs/cli_hello_greeting/12_command_review_result.md`（164行付近）「全21件のテスト」

当時のレビュー結果の記述で、現在のテスト総数とは無関係です。
**これは管理記録（履歴）なので変更不要**です（下記「修正対象外」参照）。優先度 低（＝対象外）

---

## 修正対象外とする履歴資料

古い記述を確認しましたが、**当時の事実として維持すべきもの**です。
古い仕様が書かれていることだけを理由に、現在仕様へ書き換えません。

| 対象 | 理由 |
|---|---|
| `docs/context/work_notes/` 配下すべて | 作業経緯の記録。特に `20260829_model_auto_selection/` は `role_fixed` の設計・実装・削除の経緯を含むが、当時の判断としてそのまま残す |
| `docs/context/ai_work_logs/` 配下 | 旧方式として凍結済みと明記されている |
| `docs/context/rejected_verbose_option.md` | 却下案の記録 |
| 各 feature の `gates/` 配下の Gate記録 | **immutable。** `gate_record/v1` のものを含め書き換えない |
| 各 feature の `25_review_result.md`、`12_command_review_result.md` | 当時のレビュー結果という管理記録。テスト件数などが古くても事実（L-2） |
| `docs/cli_*/bugs/` 配下 | 当時のバグ対応記録 |

---

## 人間判断が必要なもの（履歴か現行かが割れる）

| 対象 | 論点 |
|---|---|
| `docs/cli_uppercase_text/features/uppercase/tasks.md`（「G0 Gate」） | `tasks.md` は**現在地メモ**であり履歴資料ではない。ただしこの feature 自体が検証残骸なので、「文言を直す」より「feature ごと扱いを決める」のが筋（M-7） |
| `cli_text_masker` / `cli_mask_rework` | 検証残骸として整理するか、オートモードの正式サンプルへ昇格させるか。**昇格させるなら README 等への案内が必要** |

---

## すでに現行仕様と整合しているファイル

調査中に確認できたもので、**修正作業で壊さないよう注意が必要**です。

- `docs/rules/project/70_feature_loop.md`（正本。実装・テストと一致）
- `docs/rules/project/20_workflow.md` の**内容**（承認を置く工程、実装開始条件の表とも正確。問題は M-2 の位置づけのみ）
- `docs/rules/project/50_ai_permissions.md`（Gate記録の更新権限、CP1 / CP3 の承認欄）
- `docs/rules/project/25_review_policy.md`（Gate判定と評価値4値の関係、集計への影響なし）
- `docs/rules/project/10_document_structure.md`（`gates/`、`tests/tools/` を収録済み。誤りは M-1 の `g0` 例のみ）
- `docs/rules/project/15_document_templates.md`（Gate記録テンプレートの対応表）
- `docs/rules/core/20_approval_and_review.md`（収束ループと Gate を core レベルで定義済み）
- `prompts/README.md`（オートモードを先頭に配置済み）
- `prompts/run_stage.md` / `prompts/review_stage.md` / `prompts/implement_feature.md` / `prompts/create_review_checklist.md`
- `docs/templates/README.md` / `docs/templates/gate_record_template.md`
- `tools/README.md`
